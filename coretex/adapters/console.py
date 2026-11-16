from coretex.core.domain import Reading
from coretex.core.services import TelemetryListener



#Observer - concrete listener (world) (mb create interface in service.py)
class ConsoleListener(TelemetryListener):
    def on_reading(self, reading: Reading) -> None:
        print(f"{reading.timestamp:%H:%M:%S}  {reading.device_id}  {reading.type} = {reading.value}")
