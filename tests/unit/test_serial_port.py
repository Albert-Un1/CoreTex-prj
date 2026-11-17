from coretex.adapters.message_processor import TextMessageProcessor
from coretex.adapters.serial_port import SerialTelemetryAdapter
from coretex.core.ports import TelemetryPort


class FakeTelemetry(TelemetryPort):
    REJECTED_VALUE = -127.0

    def __init__(self):
        self.received = []

    def receive(self, reading):
        if reading.value == self.REJECTED_VALUE:
            raise ValueError("rejected by the core")
        self.received.append(reading.value)


def make_adapter(core):
    return SerialTelemetryAdapter("COM_TEST", TextMessageProcessor("sensor-1"), core)


def test_valid_line_reaches_core():
    core = FakeTelemetry()

    make_adapter(core).handle_line("T:21.0")

    assert core.received == [21.0]


def test_bad_lines_do_not_stop_the_adapter():
    core = FakeTelemetry()
    adapter = make_adapter(core)

    adapter.handle_line("T:abc")   #malformed
    adapter.handle_line("T:-127")  #rejected by the core
    adapter.handle_line("T:22.0")  #processed

    assert core.received == [22.0]
