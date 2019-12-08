import logging
from digi.xbee.devices import XBeeDevice

logger = logging.getLogger()


class XBee:
    def __init__(self, port, baud_rate=9600):
        self._device = XBeeDevice(port, baud_rate)

    def open(self):
        self._device.open()
        self._device.add_data_received_callback(self._on_data_received)

    def close(self):
        self._device.close()

    def send_broadcast(self, mac_address, data):
        self._device.send_data_broadcast(data)

    def send(self, data):
        pass

    def on_message_received(self, remote, data):
        pass

    def _on_data_received(self, message):
        self.on_message_received(message.get_64bit_addr(), message.data)
