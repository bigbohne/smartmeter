import io
import re
import serial
import os
import threading
from flask import Flask
import time

def parse_struct(input: io.BytesIO, level: int = 0):
    header = input.read(1)[0]
    type = (header & 0xF0) >> 4
    length = header & 0x0F

    prefix = " " * level
    #print(f"{prefix}header: {header:02x}, type: {type}, length: {length}, level: {level}")



    if header == 0x00:
        return parse_struct(input=input, level=level)
    elif type == 8:
        return None
    elif type == 7:
        return parse_list(input, length, level=level)
    elif type == 0: # Octet string
        return parse_octet_string(input, length - 1)
    elif type == 5:
        return parse_signed(input, length - 1)
    elif type == 6:
        return parse_unsigned(input, length - 1)
    else:
        #print(f"Unknown type: {type}, {length}")
        return None

def parse_list(input: io.BytesIO, length: int, level: int):
    prefix = " " * level
    #print(f"{prefix}List {length}")
    return [parse_struct(input, level=level+1) for i in range(length)]

def parse_octet_string(input: io.BytesIO, length: int):
    return input.read(length)

def parse_unsigned(input: io.BytesIO, length: int):
    return int.from_bytes(input.read(length), byteorder='big', signed=False)

def parse_signed(input: io.BytesIO, length: int):
    return int.from_bytes(input.read(length), byteorder='big', signed=True)


def read_message(input: io.BytesIO):
    msg_re = re.compile(b'\x1b\x1b\x1b\x1b\x01\x01\x01\x01(.*)\x1b\x1b\x1b\x1b\x1a')

    buffer = b""

    # Find start
    start_found = False
    while not start_found:
        c = input.read(1)
        buffer = buffer + c

        if b'\x1b\x1b\x1b\x1b\x01\x01\x01\x01' in buffer:
            start_found = True

    return parse_struct(input)
        
        
        

def create_measurement():
    with serial.Serial('/dev/ttyUSB0', 9600, timeout=10) as thefile:
        the_message = read_message(thefile)

        result = {}

        for entry in the_message[5][3][1][4]:
            obis = f"{entry[0][2]}.{entry[0][3]}.{entry[0][4]}"
            value = entry[5]

            result[obis] = value

        return result

def store_measurement(measurement):
    with open("metrics.tmp", "w") as m:
        m.write(f'smartmeter_power{{meter="twietenhof" phase="Total"}} {measurement["16.7.0"]} \n')
        m.write(f'smartmeter_counter{{meter="twietenhof" obis="1.8.0"}} {measurement["1.8.0"] / 10000.0} \n')
        m.write(f'smartmeter_counter{{meter="twietenhof" obis="1.8.1"}} {measurement["1.8.1"] / 10000.0} \n')
        m.write(f'smartmeter_counter{{meter="twietenhof" obis="1.8.2"}} {measurement["1.8.2"] / 10000.0} \n')
        m.write(f'smartmeter_counter{{meter="twietenhof" obis="2.8.0"}} {measurement["2.8.0"] / 10000.0} \n')
        m.write(f'smartmeter_counter{{meter="twietenhof" obis="2.8.1"}} {measurement["2.8.1"] / 10000.0} \n')
        m.write(f'smartmeter_counter{{meter="twietenhof" obis="2.8.2"}} {measurement["2.8.2"] / 10000.0} \n')

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
    threading.Thread(target=app.run, kwargs={'host':"0.0.0.0", 'port': "8080"}, daemon=True).start()

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
