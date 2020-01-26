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


class Echo:
    def __init__(self, xbee: XBee):
        self._device = xbee
        self._device.on_message_received = self.on_message_received

    def send(self, remote_address: bytearray, data: bytearray):
        try:
            self._device.send(remote_address, data)
            logging.info("Send\t%s\t%s", remote_address, data)
        except Exception as e:
            logging.error("Send error\t%s\t%s", remote_address, e)

    def on_message_received(self, remote_address: bytearray, data: bytearray):
        logging.info("Receive\t%s\t%s", remote_address, data)
        self.send(remote_address, data)


def main():
    parser = ArgumentParser()
    parser.add_argument('--device', required=True)

    args = parser.parse_args()

    xbee = XBee(args.device, baud_rate=9600)
    xbee.open()

    Echo(xbee)

    input()

    xbee.close()


if __name__ == '__main__':
    main()
