#test run - builds the core and sends fake readings

from datetime import datetime

from coretex.adapters.console import ConsoleListener
from coretex.adapters.memory_repository import InMemoryRepository
from coretex.core.domain import Reading, TemperatureSensor, UnknownDeviceError
from coretex.core.factory import TemperatureSensorCreator
from coretex.core.services import DeviceService, StorageListener, TelemetryService



def main() -> None:
    #build the core and connect it to the adapters
    repository = InMemoryRepository()
    devices = DeviceService(repository, [TemperatureSensorCreator()])
    telemetry = TelemetryService(repository)

    telemetry.subscribe(StorageListener(repository))
    telemetry.subscribe(ConsoleListener())

    #register a fake device
    devices.register_device(TemperatureSensor.TYPE, "nano-1", "Test sensor", "Desk")

    #send fake readings, including bad ones
    fake_readings = [
        ("nano-1", 22.5),
        ("nano-1", 23.1),
        ("nano-1", -127),   # disconnected sensor - must be rejected
        ("ghost", 20.0),    # unknown device - must be rejected
        ("nano-1", 23.8),
    ]
    for device_id, value in fake_readings:
        reading = Reading(device_id, "temperature", value, datetime.now())
        try:
            telemetry.receive(reading)
        except (ValueError, UnknownDeviceError) as error:
            print(f"Rejected: {error}")

    #check what was stored
    print(f"Stored readings: {len(repository.find_readings('nano-1'))}")


if __name__ == "__main__":
    main()
