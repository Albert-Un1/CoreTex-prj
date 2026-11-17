from abc import ABC, abstractmethod

from coretex.core.domain import Device, TemperatureSensor


#Creator
class DeviceCreator(ABC):

    @abstractmethod
    def device_type(self) -> str:
        pass

    @abstractmethod
    def create_device(self, device_id: str, name: str, room: str) -> Device:
        pass

    def create(self, device_id: str, name: str, room: str, address: str) -> Device:
        for field, value in (("id", device_id), ("name", name), ("room", room), ("address", address)):
            if not value.strip():
                raise ValueError(f"Device {field} must not be blank")
        return self.create_device(device_id, name, room, address)

#ConcreteCreator
class TemperatureSensorCreator(DeviceCreator):
    def device_type(self) -> str:
        return TemperatureSensor.TYPE

    def create_device(self, device_id: str, name: str, room: str, address: str) -> Device:
        return TemperatureSensor(device_id, name, room, address)
