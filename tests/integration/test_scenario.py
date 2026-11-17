#test whole core with an in-memory repository

from datetime import datetime

import pytest

from coretex.adapters.memory_repository import InMemoryRepository
from coretex.core.domain import Device, Reading, TemperatureSensor, UnknownDeviceError
from coretex.core.factory import TemperatureSensorCreator
from coretex.core.ports import DeviceConnectionPort
from coretex.core.services import DeviceService, StorageListener, TelemetryService


class FakeConnection(DeviceConnectionPort):
    def __init__(self):
        self.listened = []

    def listen(self, device: Device) -> None:
        self.listened.append(device.device_id)

#build the core and connect it to the adapters
def build_core():
    repository = InMemoryRepository()
    devices = DeviceService(repository, FakeConnection(), [TemperatureSensorCreator()])
    telemetry = TelemetryService(repository)
    telemetry.subscribe(StorageListener(repository))

    #register a fake device
    devices.register_device(TemperatureSensor.TYPE, "sensor-1", "Test sensor", "Desk", "COM_TEST")
    return repository, telemetry


#data map
def temperature(device_id: str, value: float) -> Reading:
    return Reading(device_id, "temperature", value, datetime.now())



def test_valid_readings_are_stored():
    repository, telemetry = build_core()

    telemetry.receive(temperature("sensor-1", 22.5))
    telemetry.receive(temperature("sensor-1", 23.1))

    stored = [reading.value for reading in repository.find_readings("sensor-1")]
    assert stored == [22.5, 23.1]



def test_disconnected_sensor_value_is_rejected():
    repository, telemetry = build_core()

    with pytest.raises(ValueError):
        telemetry.receive(temperature("sensor-1", -127))

    assert repository.find_readings("sensor-1") == []



def test_reading_from_unknown_device_is_rejected():
    repository, telemetry = build_core()

    with pytest.raises(UnknownDeviceError):
        telemetry.receive(temperature("ghost", 20.0))

    assert repository.find_readings("ghost") == []
