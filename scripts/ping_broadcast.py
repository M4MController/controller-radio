import logging
import struct
import sys
import time

from argparse import ArgumentParser
from datetime import datetime
from random import randint

from radio.xbee import XBee

logging.basicConfig(
    stream=sys.stdout,
    level=logging.CRITICAL,
    format='%(asctime)s [%(levelname)s] %(message)s',
)


class Ping:
    _map = {}

    def __init__(self, xbee: XBee):
        self._device = xbee
        self._device.on_message_received = self.on_message_received

    def ping(self):
        value = randint(0, 4000000)
        self._map[value] = datetime.now()
        data = bytearray(struct.pack('i', value))
        try:
            self._device.send_broadcast(data)
            logging.info("Send\t%s\t%d", value)
        except Exception as e:
            logging.error("Send error\t%s\t%s", e)

    def on_message_received(self, remote_address: bytearray, data: bytearray):
        value, = struct.unpack("i", data)
        time = self._map.get(value, None)
        if time is not None:
            logging.critical("Ping\t%s\t%s ms", remote_address, (datetime.now() - time).microseconds)
        else:
            logging.critical("Invalid pong\t %s", value)


def main():
    parser = ArgumentParser()
    parser.add_argument('--device', required=True)
    parser.add_argument('--init', action='store_true')

    args = parser.parse_args()

    xbee = XBee(args.device, baud_rate=9600)
    xbee.open()

    ping = Ping(xbee)

    while True:
        ping.ping()

    xbee.close()


if __name__ == '__main__':
    main()
