from pymodbus.constants import Endian
from pymodbus.client import ModbusTcpClient
from pymodbus.payload import BinaryPayloadDecoder

from flask import Flask

import threading
import time
import os

def read_float(client: ModbusTcpClient, address: int) -> float:
    response = client.read_holding_registers(address=address, count=4, slave=1)
    decoder = BinaryPayloadDecoder.fromRegisters(response.registers, byteorder=Endian.Big, wordorder=Endian.Big)
    return decoder.decode_32bit_float()

def create_measurement():
    client = ModbusTcpClient(host="192.168.2.232", port=9999)
    client.connect()

    result = {}
    result["total_active_energy"] = read_float(client=client, address=0x100)
    result["forward_active_energy"] = read_float(client=client, address=0x108)
    result["reverse_active_energy"] = read_float(client=client, address=0x110)

    result["total_active_power"] = read_float(client=client, address=0x1c) * 1000
    result["L1_active_power"] = read_float(client=client, address=0x1e) * 1000
    result["L2_active_power"] = read_float(client=client, address=0x20) * 1000
    result["L3_active_power"] = read_float(client=client, address=0x22) * 1000

    result["grid_frequency"] = read_float(client=client, address=0x14)

    client.close()

    return result

def store_measurement(measurement):
    with open("metrics.tmp", "w") as m:
        m.write(f'smartmeter_power{{meter="boffi_office" phase="Total"}} {measurement["total_active_power"]} \n')
        m.write(f'smartmeter_power{{meter="boffi_office" phase="L1"}} {measurement["L1_active_power"]} \n')
        m.write(f'smartmeter_power{{meter="boffi_office" phase="L2"}} {measurement["L2_active_power"]} \n')
        m.write(f'smartmeter_power{{meter="boffi_office" phase="L3"}} {measurement["L3_active_power"]} \n')

        m.write(f'smartmeter_counter{{meter="boffi_office" direction="active"}} {measurement["total_active_energy"]} \n')
        m.write(f'smartmeter_counter{{meter="boffi_office" direction="forward"}} {measurement["forward_active_energy"]} \n')
        m.write(f'smartmeter_counter{{meter="boffi_office" direction="reverse"}} {measurement["reverse_active_energy"]} \n')

        m.write(f'smartmeter_frequency{{meter="boffi_office"}} {measurement["grid_frequency"]} \n')

    os.rename("metrics.tmp", "metrics")
        
def clear_metrics():
    with open("metrics", "w") as thefile:
        pass

app = Flask(__name__)

@app.get("/metrics")
def metrics():
    with open("metrics") as m:
        return m.read()

if __name__ == "__main__":
    threading.Thread(target=app.run, kwargs={'host':"0.0.0.0", 'port': "8082"}, daemon=True).start()

    while True:
        ts = int(time.time())
        sleep_time = 15 - (ts % 15)
        next_minute = ts + sleep_time

        print(next_minute, sleep_time)
        time.sleep(sleep_time)

        try:
            measurement = create_measurement()
            store_measurement(measurement)
        except Exception as ex:
            print(ex)
            clear_metrics()