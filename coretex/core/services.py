from abc import ABC, abstractmethod

from coretex.core.domain import Device, Reading, UnknownDeviceError
from coretex.core.factory import DeviceCreator
from coretex.core.ports import DevicePort, RepositoryPort, TelemetryPort


#Observer super
class TelemetryListener(ABC):
    @abstractmethod
    def on_reading(self, reading: Reading) -> None:
        pass

#Observer Subject - Checks and passes
class TelemetryService(TelemetryPort):
    def __init__(self, repository: RepositoryPort) -> None:
        self._repository = repository
        self._listeners: list[TelemetryListener] = []

    def subscribe(self, listener: TelemetryListener) -> None:
        self._listeners.append(listener)

    def unsubscribe(self, listener: TelemetryListener) -> None:
        self._listeners.remove(listener)

    def receive(self, reading: Reading) -> None:
        device = self._repository.find_device(reading.device_id)
        if device is None:
            raise UnknownDeviceError(reading.device_id)
        if not device.accepts(reading):
            raise ValueError(f"{device.device_id} rejected {reading.type}={reading.value}")

        for listener in self._listeners:
            listener.on_reading(reading)

#Observer concrete listener
class StorageListener(TelemetryListener):
    def __init__(self, repository: RepositoryPort) -> None:
        self._repository = repository

    def on_reading(self, reading: Reading) -> None:
        self._repository.save_reading(reading)

class DeviceService(DevicePort):
    def __init__(self, repository: RepositoryPort, creators: list[DeviceCreator]) -> None:
        self._repository = repository
        self._creators = {}
        for creator in creators:
            self._creators[creator.device_type()] = creator

    def register_device(self, device_type: str, device_id: str, name: str, room: str) -> Device:
        creator = self._creators.get(device_type)
        if creator is None:
            raise ValueError(f"Unknown device type: {device_type}")

        if self._repository.find_device(device_id) is not None:
            raise ValueError(f"Device already registered: {device_id}")

        device = creator.create(device_id, name, room)
        self._repository.save_device(device)
        return device

    def list_devices(self) -> list[Device]:
        return self._repository.find_all_devices()
