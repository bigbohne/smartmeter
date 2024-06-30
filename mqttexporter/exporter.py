import aiomqtt
import asyncio

from converter import ShellyPowerConverter, ShellyEnergyConverter, SmartmeterPowerConverter, SmartmeterCounterConverter, SmartmeterFrequencyConverter
from server import create_app
from storage import MetricStorage

async def main():
    storage = MetricStorage()
    await asyncio.gather(mqtt_listener(storage), create_app(storage).run_task())
        

async def mqtt_listener(storage: MetricStorage):
    shelly_power_conv = ShellyPowerConverter()
    shelly_energy_conv = ShellyEnergyConverter()
    smartmeter_power_conv = SmartmeterPowerConverter()
    smartmeter_counter_conv = SmartmeterCounterConverter()
    smartmeter_frequency_conv = SmartmeterFrequencyConverter()

    async with aiomqtt.Client("192.168.2.244") as client:
        async with client.messages() as messages:
            await client.subscribe("shellies/#")
            await client.subscribe("smartmeter/#")

            async for message in messages:
                metrics = [
                        shelly_power_conv.convert(message=message),
                        shelly_energy_conv.convert(message=message),
                        smartmeter_power_conv.convert(message=message),
                        smartmeter_counter_conv.convert(message=message),
                        smartmeter_frequency_conv.convert(message=message)]
                metrics = [metric for metric in metrics if metric is not None]

                for metric in metrics:
                    storage.push(metric=metric)


if __name__ == "__main__":
    asyncio.run(main(), debug=True)
