from typing import List
import requests
from requests.auth import HTTPBasicAuth
from flask import Flask

import threading
import time
import os
import re

def create_measurement():
    basic = HTTPBasicAuth('admin', 'admin')
    response: requests.Response = requests.get("http://192.168.2.129/status.html", stream=True, timeout=10, auth=basic)

    regex = re.compile('var (\S+) = \"([\d\.]+)\"')

    lines: List = [line.decode() for line in response.iter_lines() if "var webdata_" in line.decode()]
    matched_lines = filter(lambda elem: elem is not None, map(regex.match, lines))

    result = {elem[1] : float(elem[2]) for elem in matched_lines}

    return result

def retry_create_measurement():
    for i in range(5):
        try:
            return create_measurement()
        except:
            time.sleep(1)

    raise ConnectionError()

def store_measurement(measurement):
    with open("metrics.tmp", "w") as m:
        m.write(f'solar_power{{inverter="boffi_red" phase="Total"}} {measurement["webdata_now_p"]} \n')
        m.write(f'solar_energy{{inverter="boffi_red" phase="Total"}} {measurement["webdata_total_e"]} \n')

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
    threading.Thread(target=app.run, kwargs={'host':"0.0.0.0", 'port': "8083"}, daemon=True).start()

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