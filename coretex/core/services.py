from coretex.core.domain import Device
from coretex.core.factory import DeviceCreator
from coretex.core.ports import DevicePort, RepositoryPort



class DeviceService(DevicePort):
    def __init__(self, repository: RepositoryPort, creators: list[DeviceCreator]) -> None:
        self._repository = repository
        self._creators = {}
        for creator in creators:
            self._creators[creator.device_type()] = creator

    def register_device(self, device_type: str, device_id: str, name: str, room: str) -> Device:
        creator = self._creators.get(device_type)
        if creator is None:
            raise ValueError(f"Unknown device type: {device_type}")

        if self._repository.find_device(device_id) is not None:
            raise ValueError(f"Device already registered: {device_id}")

        device = creator.create(device_id, name, room)
        self._repository.save_device(device)
        return device

    def list_devices(self) -> list[Device]:
        return self._repository.find_all_devices()
