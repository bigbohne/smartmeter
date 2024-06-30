from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Union, Optional
from aiomqtt import Message
from urllib.parse import urlparse

@dataclass(eq=False)
class Metric:
    metric: str
    tags: Dict[str, str]
    value: Union[int, float]

    def __eq__(self, other: object) -> bool:
        return (self.metric == other.metric) and (self.tags == other.tags)
    
    def __str__(self) -> str:
        tags = ",".join([f"{key}=\"{value}\"" for key, value in self.tags.items()])
        return f"{self.metric}{{{tags}}} {self.value}"


class Converter(ABC):
    @abstractmethod
    def convert(self, message: Message) -> Optional[Metric]:
        pass


class ShellyPowerConverter(Converter):
    def convert(self, message: Message) -> Optional[Metric]:
        if message.topic.matches("shellies/+/relay/+/power"):
            return Metric(metric="shelly_power", value=float(message.payload), tags={
                "sensor": message.topic.value.split("/")[1],
                "relay": message.topic.value.split("/")[3],
                "sensor_type": "shelly",
                "topic": message.topic.value
            })
        
        return None
    
    
class ShellyEnergyConverter(Converter):
    def convert(self, message: Message) -> Optional[Metric]:
        if message.topic.matches("shellies/+/relay/+/energy"):
            return Metric(metric="shelly_energy", value=float(message.payload), tags={
                "sensor": message.topic.value.split("/")[1],
                "relay": message.topic.value.split("/")[3],
                "sensor_type": "shelly",
                "topic": message.topic.value
            })
        
        return None
    
class SmartmeterPowerConverter(Converter):
    def convert(self, message: Message) -> Optional[Metric]:
        if message.topic.matches("smartmeter/+/power/+"):
            # smartmeter_power{meter="boffi_oben" phase="Total"} 0.201
            return Metric(metric="smartmeter_power", value=float(message.payload), tags={
                "meter": message.topic.value.split("/")[1],
                "phase": message.topic.value.split("/")[3],
            })
        
        return None
    
class SmartmeterCounterConverter(Converter):
    def convert(self, message: Message) -> Optional[Metric]:
        if message.topic.matches("smartmeter/+/counter/+"):
            return Metric(metric="smartmeter_counter", value=float(message.payload), tags={
                "meter": message.topic.value.split("/")[1],
                "obis": message.topic.value.split("/")[3],
            })
        
        return None
    
class SmartmeterFrequencyConverter(Converter):
    def convert(self, message: Message) -> Optional[Metric]:
        if message.topic.matches("smartmeter/+/frequency"):
            return Metric(metric="smartmeter_frequency", value=float(message.payload), tags={
                "meter": message.topic.value.split("/")[1],
            })
        
        return None