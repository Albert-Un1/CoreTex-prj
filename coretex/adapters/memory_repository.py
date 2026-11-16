from coretex.core.domain import Device, Reading
from coretex.core.ports import RepositoryPort


#Outbound adapter - memory
class InMemoryRepository(RepositoryPort):
    def __init__(self) -> None:
        self._devices: dict[str, Device] = {} #str = device.id
        self._readings: list[Reading] = []

    def save_device(self, device: Device) -> None:
        self._devices[device.device_id] = device

    def find_device(self, device_id: str) -> Device | None:
        return self._devices.get(device_id)

    def find_all_devices(self) -> list[Device]:
        return list(self._devices.values())

    def save_reading(self, reading: Reading) -> None:
        self._readings.append(reading)

    def find_readings(self, device_id: str) -> list[Reading]:
        return [reading for reading in self._readings if reading.device_id == device_id]
