from abc import ABC, abstractmethod

from coretex.core.domain import Device, Reading



#Inbound ports:

class TelemetryPort(ABC):

    @abstractmethod
    def receive(self, reading: Reading) -> None:
        pass

class DevicePort(ABC):

    @abstractmethod
    def register_device(self, device_type: str, device_id: str, name: str, room: str) -> Device:
        pass

    @abstractmethod
    def list_devices(self) -> list[Device]:
        pass

#Outbound port:

class RepositoryPort(ABC):

    @abstractmethod
    def save_device(self, device: Device) -> None:
        pass

    @abstractmethod
    def find_device(self, device_id: str) -> Device | None:
        pass

    @abstractmethod
    def find_all_devices(self) -> list[Device]:
        pass

    @abstractmethod
    def save_reading(self, reading: Reading) -> None:
        pass

    @abstractmethod
    def find_readings(self, device_id: str) -> list[Reading]:
        pass
