import logging
import typing

from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice
from digi.xbee.models.address import XBee64BitAddress

logger = logging.getLogger()


class XBee:
    def __init__(self, port: str, baud_rate: int = 9600):
        self._device = XBeeDevice(port, baud_rate)

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
        data = self._normalize_data(data)
        remote_device = RemoteXBeeDevice(self._device, x64bit_addr=XBee64BitAddress(remote_address))
        self._device.send_data(remote_device, data)

    def on_message_received(self, remote_address: bytearray, data: bytearray):
        pass

    def _on_data_received(self, message):
        self.on_message_received(message.remote_device.get_64bit_addr().address, message.data)
