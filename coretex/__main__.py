#run with: python -m coretex

import logging

from coretex.adapters.console import ConsoleListener, CoreTexShell
from coretex.adapters.memory_repository import InMemoryRepository
from coretex.adapters.serial_port import SerialConnectionAdapter, available_ports
from coretex.core.factory import TemperatureSensorCreator
from coretex.core.services import DeviceService, StorageListener, TelemetryService


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    #outbound adapters and core
    repository = InMemoryRepository()
    telemetry = TelemetryService(repository)
    connection = SerialConnectionAdapter(telemetry)
    devices = DeviceService(repository, connection, [TemperatureSensorCreator()])

    #observers
    display = ConsoleListener()
    telemetry.subscribe(StorageListener(repository))
    telemetry.subscribe(display)

    #inbound adapter - cli
    CoreTexShell(devices, display, available_ports).cmdloop()


if __name__ == "__main__":
    main()
