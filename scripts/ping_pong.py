import logging
import struct
import sys

from argparse import ArgumentParser

from radio.xbee import XBee

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
)


class PingPong:
    def __init__(self, xbee: XBee):
        self._device = xbee
        self._device.on_message_received = self.on_message_received

    def init(self):
        self._device.send_broadcast(bytearray(struct.pack('i', 0)))

    def send(self, remote_address: bytearray, value: bytearray):
        data = bytearray(struct.pack('i', value))
        self._device.send(remote_address, data)
        logging.info("Send\t%s\t%d", remote_address, value)

    def on_message_received(self, remote_address: bytearray, data: bytearray):
        value, = struct.unpack("i", data)
        logging.info("Receive\t%s\t%d", remote_address, value)
        self.send(remote_address, value + 1)


def main():
    parser = ArgumentParser()
    parser.add_argument('--device', required=True)
    parser.add_argument('--init', action='store_true')

    args = parser.parse_args()

    xbee = XBee(args.device, baud_rate=9600)
    xbee.open()

    ping_pong = PingPong(xbee)

    if args.init:
        ping_pong.init()

    input()

    xbee.close()


if __name__ == '__main__':
    main()
