import cmd
from collections.abc import Callable

from coretex.core.domain import Reading, UnknownDeviceError
from coretex.core.ports import DevicePort
from coretex.core.services import TelemetryListener


#Observer - concrete listener (world) (mb create interface in service.py)
class ConsoleListener(TelemetryListener):
    def __init__(self) -> None:
        self.enabled = False

    def on_reading(self, reading: Reading) -> None:
        if self.enabled:
            print(f"{reading.timestamp:%H:%M:%S} | {reading.device_id} | {reading.type} = {reading.value}")


#inbound adapter - cli
class CoreTexShell(cmd.Cmd):

    intro = "CoreTex. Type help to list commands."
    prompt = "coretex> "

    def __init__(
        self,
        devices: DevicePort,
        display: ConsoleListener,
        list_ports: Callable[[], list[str]],
    ) -> None:
        super().__init__()
        self._devices = devices
        self._display = display
        self._list_ports = list_ports

    #list for available
    def do_ports(self, arg: str) -> None:
        for port in self._list_ports():
            print(f"{port}")

    #list device types
    def do_types(self, arg: str) -> None:
        for device_type in self._devices.device_types():
            print(f" {device_type}")

    #add device
    def do_add(self, arg: str) -> None:
        parts = arg.split()
        if len(parts) != 5:
            print("Usage: add TEMPERATURE_SENSOR sensor-1 COM5 Sensor Desk")
            return
        device_type, device_id, address, name, room = parts
        try:
            self._devices.register_device(device_type, device_id, name, room, address)
            print(f"Added {device_id} on {address}.")
        except ValueError as error:
            print(f"Error: {error}")

    #list devices and status
    def do_devices(self, arg: str) -> None:
        for device in self._devices.list_devices():
            status = self._devices.get_status(device.device_id)
            print(f"{device.device_id:<12} {device.device_type():<20} {device.address:<6} {status.value}")

    #start listening (id)
    def do_listen(self, arg: str) -> None:
        device_id = arg.strip()
        try:
            self._devices.start_listening(device_id)
            print(f"Listening to {device_id}. Type watch to see the data.")
        except UnknownDeviceError as error:
            print(f"Error: {error}")

    #show incoming readings (until enter key pressed)
    def do_watch(self, arg: str) -> None:
        self._display.enabled = True
        input("Showing readings. Press Enter to stop.\n")
        self._display.enabled = False

    #exit
    def do_quit(self, arg: str) -> bool:
        return True
