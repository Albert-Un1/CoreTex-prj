from abc import ABC, abstractmethod
from datetime import datetime

from coretex.core.domain import Reading


#Adapter pattern - device message into a Reading obj
class MessageProcessor(ABC):

    @abstractmethod
    def to_reading(self, message: str) -> Reading | None:
        pass


#Adapter pattern - Reading filtering
class TextMessageProcessor(MessageProcessor):

    def __init__(self, device_id: str) -> None:
        self._device_id = device_id

    def to_reading(self, message: str) -> Reading | None:
        if not message.startswith("T:"):
            return None

        value = float(message[2:])
        return Reading(self._device_id, "temperature", value, datetime.now())
