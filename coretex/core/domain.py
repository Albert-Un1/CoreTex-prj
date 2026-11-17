from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


@dataclass(frozen=True)
class Reading:
    device_id: str #which device sent
    type: str #what was measured
    value: float #the value
    timestamp: datetime #when it was measured

#connection status
class DeviceStatus(Enum):
    STOPPED = "STOPPED"  #added, idle
    OFFLINE = "OFFLINE"  #listening, but no reading
    ONLINE = "ONLINE"    #listening, reading arrived

#Product
class Device(ABC):
    def __init__(self, device_id: str, name: str, room: str, address: str) -> None:
        self.device_id = device_id
        self.name = name
        self.room = room
        self.address = address

    @abstractmethod
    def device_type(self) -> str:
        pass

    @abstractmethod
    def accepts(self, reading: Reading) -> bool:
        pass

#ConcreteProduct
class TemperatureSensor(Device):
    TYPE = "TEMPERATURE_SENSOR"
    MIN_C = -55.0
    MAX_C = 125.0

    def device_type(self) -> str:
        return self.TYPE

    def accepts(self, reading: Reading) -> bool:
        return reading.type == "temperature" and self.MIN_C <= reading.value <= self.MAX_C

#Device not registered
class UnknownDeviceError(Exception):
    def __init__(self, device_id: str) -> None:
        super().__init__(f"Unknown device: {device_id}")

