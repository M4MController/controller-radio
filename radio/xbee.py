import asyncio
import logging
import typing

from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice
from digi.xbee.models.address import XBee64BitAddress

logger = logging.getLogger()


def get_address(device) -> bytearray:
    return device.get_64bit_addr().address


class XBee:
    def __init__(self, port: str, baud_rate: int = 9600):
        self._device = XBeeDevice(port, baud_rate)

    @classmethod
    def _normalize_data(self, data: typing.Union[bytearray, bytes]):
        if isinstance(data, bytes):
            data = bytearray(data)
        return data

    def open(self):
        self._device.open()
        self._device.add_data_received_callback(self._on_data_received)

    def close(self):
        self._device.close()

    def send_broadcast(self, data: typing.Union[bytearray, bytes]):
        data = self._normalize_data(data)
        self._device.send_data_broadcast(data)

    def send(self, remote_address: bytearray, data: typing.Union[bytearray, bytes]):
        data = XBee._normalize_data(data)
        remote_device = RemoteXBeeDevice(self._device, x64bit_addr=XBee64BitAddress(remote_address))
        self._device.send_data(remote_device, data)

    async def discover_first_remote_device(self, discovery_timeout=25) -> typing.Optional[bytearray]:
        network = self._device.get_network()
        network.set_discovery_timeout(discovery_timeout)
        network.start_discovery_process()
        await asyncio.sleep(1)
        while network.is_discovery_running() or not network.get_devices():
            await asyncio.sleep(1)
        network.stop_discovery_process()

        devices = network.get_devices()
        return get_address(devices[0]) if devices else None

    def on_message_received(self, remote_address: bytearray, data: bytearray):
        pass

    def _on_data_received(self, message):
        self.on_message_received(get_address(message.remote_device), message.data)
