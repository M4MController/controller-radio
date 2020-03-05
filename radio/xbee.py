import asyncio
import logging
import random
import typing

from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice
from digi.xbee.models.address import XBee64BitAddress

from serializer import BaseModel

logger = logging.getLogger()


def get_address(device) -> bytearray:
    return device.get_64bit_addr().address


class InitFrame(BaseModel):
    fields = {
        'id': int,
        'size': int,
    }


class Frame(BaseModel):
    fields = {
        'id': int,
        'data': bytearray,
    }


class XBee:
    _buffer = {}

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

        id = random.randint(0, 4000000)
        init_frame = InitFrame(id=id, size=len(data))

        self._device.send_data(remote_device, init_frame.serialize())

        sent = 0
        while sent < len(data):
            s = data[sent:sent + 50]
            frame = Frame(id=id, data=s)

            self._device.send_data(remote_device, frame.serialize())
            sent += len(s)

    async def discover_first_remote_device(self, discovery_timeout=25) -> typing.Optional[bytearray]:
        network = self._device.get_network()
        network.set_discovery_timeout(discovery_timeout)
        network.start_discovery_process()
        await asyncio.sleep(1)
        while network.is_discovery_running() and not network.get_devices():
            await asyncio.sleep(1)
        network.stop_discovery_process()

        devices = network.get_devices()
        return get_address(devices[0]) if devices else None

    def on_message_received(self, remote_address: bytearray, data: bytearray):
        pass

    def _on_data_received(self, message):
        init_frame = InitFrame.deserialize(message.data)
        try:
            if init_frame.id in self._buffer:
                frame = Frame.deserialize(message.data)
                self._buffer[frame.id][1].extend(frame.data)

                full_size = self._buffer[frame.id][0]
                if len(self._buffer[frame.id][1]) >= full_size:
                    self.on_message_received(get_address(message.remote_device), self._buffer[frame.id][1][:full_size])
                    del self._buffer[frame.id]
            else:
                self._buffer[init_frame.id] = [init_frame.size, bytearray()]
        except Exception as e:
            logger.error(e)
            self._buffer.pop(init_frame.id, None)


