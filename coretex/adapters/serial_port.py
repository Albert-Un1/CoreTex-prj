import logging
import threading
import time

import serial
from serial.tools import list_ports

from coretex.adapters.message_processor import MessageProcessor, TextMessageProcessor
from coretex.core.domain import Device, UnknownDeviceError
from coretex.core.ports import DeviceConnectionPort, TelemetryPort

logger = logging.getLogger(__name__)


#names and descriptions of all COM ports - 5 for bt
def available_ports() -> list[str]:
    return [f"{port.device}  {port.description}" for port in list_ports.comports()]


#Inbound adapter - reads lines and passes readings
class SerialTelemetryAdapter:

    def __init__(
        self,
        port_name: str,
        processor: MessageProcessor,
        telemetry: TelemetryPort,
        retry_delay: float = 3.0,
    ) -> None:
        self._port_name = port_name
        self._processor = processor
        self._telemetry = telemetry
        self._retry_delay = retry_delay

    #read forever. if lost -> wait and try again
    def run(self) -> None:
        while True:
            try:
                with serial.Serial(self._port_name, 9600, timeout=1) as connection:
                    logger.info("Connected to %s", self._port_name)
                    while True:
                        line = connection.readline().decode("ascii", errors="replace").strip()
                        if line:
                            self.handle_line(line)
            except serial.SerialException as error:
                logger.warning("No connection to %s: %s", self._port_name, error)
                time.sleep(self._retry_delay)

    def handle_line(self, line: str) -> None:
        try:
            reading = self._processor.to_reading(line)
            if reading is not None:
                self._telemetry.receive(reading)
        except (ValueError, UnknownDeviceError) as error:
            logger.warning("Rejected %r: %s", line, error)

#outbound adapter - listens to device
class SerialConnectionAdapter(DeviceConnectionPort):
    def __init__(self, telemetry: TelemetryPort) -> None:
        self._telemetry = telemetry

    def listen(self, device: Device) -> None:
        reader = SerialTelemetryAdapter(device.address, TextMessageProcessor(device.device_id), self._telemetry)
        threading.Thread(target=reader.run, daemon=True).start()
