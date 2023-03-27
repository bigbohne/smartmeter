from typing import List
import requests
import re

response: requests.Response = requests.get("http://192.168.2.129/status.html", stream=True, timeout=10)

regex = re.compile('var (\S+) = \"([\d\.]+)\"')

lines: List = [line.decode() for line in response.iter_lines() if "var webdata_" in line.decode()]
matched_lines = filter(lambda elem: elem is not None, map(regex.match, lines))

data = {elem[1] : float(elem[2]) for elem in matched_lines}
print(data)