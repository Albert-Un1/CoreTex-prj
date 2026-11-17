import pytest

from coretex.adapters.message_processor import TextMessageProcessor


def test_temperature_message_becomes_reading():
    reading = TextMessageProcessor("sensor-1").to_reading("T:23.56")

    assert reading.device_id == "sensor-1"
    assert reading.type == "temperature"
    assert reading.value == 23.56


@pytest.mark.parametrize("message", ["HELLO", "B:1", "OK:ON", "E:SENSOR", ""])
def test_other_messages_are_not_readings(message):
    assert TextMessageProcessor("sensor-1").to_reading(message) is None


def test_malformed_temperature_raises():
    with pytest.raises(ValueError):
        TextMessageProcessor("sensor-1").to_reading("T:abc")
