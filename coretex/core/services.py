from abc import ABC, abstractmethod
from collections.abc import Callable
from datetime import datetime, timedelta

from coretex.core.domain import Device, DeviceStatus, Reading, UnknownDeviceError
from coretex.core.factory import DeviceCreator
from coretex.core.ports import (
    DeviceConnectionPort,
    DevicePort,
    RepositoryPort,
    TelemetryPort,
)


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
    OFFLINE_AFTER = timedelta(seconds=60)

    def __init__(
        self,
        repository: RepositoryPort,
        connection: DeviceConnectionPort,
        creators: list[DeviceCreator],
        clock: Callable[[], datetime] = datetime.now,
    ) -> None:
        self._repository = repository
        self._connection = connection
        self._creators = {creator.device_type(): creator for creator in creators}
        self._clock = clock
        self._listening: set[str] = set()

    def register_device(self, device_type: str, device_id: str, name: str, room: str, address: str) -> Device:
        creator = self._creators.get(device_type)
        if creator is None:
            raise ValueError(f"Unknown device type: {device_type}")

        if self._repository.find_device(device_id) is not None:
            raise ValueError(f"Device already registered: {device_id}")

        device = creator.create(device_id, name, room, address)
        self._repository.save_device(device)
        return device

    def list_devices(self) -> list[Device]:
        return self._repository.find_all_devices()

    def start_listening(self, device_id: str) -> None:
        device = self._require_device(device_id)
        if device_id in self._listening:
            return #already listening
        self._connection.listen(device)
        self._listening.add(device_id)

    def get_status(self, device_id: str) -> DeviceStatus:
        self._require_device(device_id)
        if device_id not in self._listening:
            return DeviceStatus.STOPPED

        readings = self._repository.find_readings(device_id)
        if not readings:
            return DeviceStatus.OFFLINE

        last_seen = readings[-1].timestamp
        if self._clock() - last_seen <= self.OFFLINE_AFTER:
            return DeviceStatus.ONLINE
        return DeviceStatus.OFFLINE

    def _require_device(self, device_id: str) -> Device:
        device = self._repository.find_device(device_id)
        if device is None:
            raise UnknownDeviceError(device_id)
        return device

    def device_types(self) -> list[str]:
        return list(self._creators)
