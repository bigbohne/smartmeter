import serial
import io
import re
import dataclasses
from typing import Dict
import time
from flask import Flask
import os
import threading
import functools

@dataclasses.dataclass
class ObisValue():
    tag: str
    value: float

def read_meter(command):
    ser = serial.serial_for_url('/dev/ttyUSB0', 9600, parity=serial.PARITY_EVEN, bytesize=serial.SEVENBITS, timeout=10)
    sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))

    sio.write(command)
    sio.flush()

    reg = re.compile("([0-9\.]+)\(([\-0-9\.]*)")

    first_line = sio.readline()
    print(first_line.strip())
    sio.write('\x06050\r\n')
    sio.flush()

    while True:
        line = sio.readline().strip()
        if len(line) == 0 or line[0] == '!':
            ser.close()
            return

        match = reg.match(line)

        if match == None:
            continue

        groups = match.groups()
        yield ObisValue(tag=groups[0], value=float(groups[1]))

@dataclasses.dataclass
class Measurement():
    PTotal: float
    PL1: float
    PL2: float
    PL3: float
    VL1: float
    VL2: float
    VL3: float
    AL1: float
    AL2: float
    AL3: float
    PfL1: float
    PfL2: float
    PfL3: float
    counter1: float
    counter2: float
    counter3: float
    frequency: float

def obis_values_to_measurement(obis_values: Dict[str, ObisValue]) -> Measurement:
    return Measurement(
            PTotal=obis_values["1.7.0"],
            PL1=obis_values["21.7.0"],
            PL2=obis_values["41.7.0"],
            PL3=obis_values["61.7.0"],
            VL1=obis_values["32.7.0"],
            VL2=obis_values["52.7.0"],
            VL3=obis_values["72.7.0"],
            AL1=obis_values["31.7.0"],
            AL2=obis_values["51.7.0"],
            AL3=obis_values["71.7.0"],
            PfL1=obis_values["33.7.0"],
            PfL2=obis_values["53.7.0"],
            PfL3=obis_values["73.7.0"],
            counter1=obis_values["1.8.0"],
            counter2=obis_values["1.8.1"],
            counter3=obis_values["1.8.2"],
            frequency=obis_values["34.7"])


def create_measurement() -> Measurement:
    values_summaries = list(read_meter("/?!\r\n"))
    values_current = list(read_meter("/2!\r\n"))

    values = values_summaries + values_current
    key_value = {value.tag: value for value in values}

    return obis_values_to_measurement(key_value)

def store_measurement(measurement: Measurement):
    with open("metrics.tmp", "w") as m:
        m.write(f'smartmeter_power{{meter="boffi_oben" phase="Total"}} {measurement.PTotal.value} \n')
        m.write(f'smartmeter_power{{meter="boffi_oben" phase="L1"}} {measurement.PL1.value} \n')
        m.write(f'smartmeter_power{{meter="boffi_oben" phase="L2"}} {measurement.PL2.value} \n')
        m.write(f'smartmeter_power{{meter="boffi_oben" phase="L3"}} {measurement.PL3.value} \n')
        
        m.write(f'smartmeter_counter{{meter="boffi_oben" obis="1.8.0"}} {measurement.counter1.value} \n')
        m.write(f'smartmeter_counter{{meter="boffi_oben" obis="1.8.1"}} {measurement.counter2.value} \n')
        m.write(f'smartmeter_counter{{meter="boffi_oben" obis="1.8.2"}} {measurement.counter3.value} \n')
        
        m.write(f'smartmeter_frequency{{meter="boffi_oben"}} {measurement.frequency.value} \n')

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
    threading.Thread(target=app.run, kwargs={'host':"0.0.0.0", 'port': "8080"}).start()

    while True:
        ts = int(time.time())
        sleep_time = 60 - (ts % 60)
        next_minute = ts + sleep_time

        print(next_minute, sleep_time)
        time.sleep(sleep_time)
        
        try:
            measurement = create_measurement()
            store_measurement(measurement)
        except Exception as ex:
            print(ex)
            clear_metrics()
