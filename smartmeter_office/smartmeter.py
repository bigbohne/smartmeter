from pymodbus.constants import Endian
from pymodbus.client import ModbusTcpClient
from pymodbus.payload import BinaryPayloadDecoder

client = ModbusTcpClient(host="192.168.2.232", port=9999)
client.connect()

response = client.read_holding_registers(address=0x1c, count=4, slave=1)
decoder = BinaryPayloadDecoder.fromRegisters(response.registers, byteorder=Endian.Big, wordorder=Endian.Big)
watt = decoder.decode_32bit_float() * 1000.0
print(f"{watt:.0f} Watt")