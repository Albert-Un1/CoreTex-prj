from abc import ABC, abstractmethod

from coretex.core.domain import Device, DeviceStatus, Reading

#Inbound ports:

class TelemetryPort(ABC):

    @abstractmethod
    def receive(self, reading: Reading) -> None:
        pass

class DevicePort(ABC):

    @abstractmethod
    def register_device(self, device_type: str, device_id: str, name: str, room: str, address: str) -> Device:
        pass

    @abstractmethod
    def list_devices(self) -> list[Device]:
        pass

    @abstractmethod
    def start_listening(self, device_id: str) -> None:
        pass

    @abstractmethod
    def get_status(self, device_id: str) -> DeviceStatus:
        pass

    @abstractmethod
    def device_types(self) -> list[str]:
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

#start receiving data from a device
class DeviceConnectionPort(ABC):
    @abstractmethod
    def listen(self, device: Device) -> None:
        pass
