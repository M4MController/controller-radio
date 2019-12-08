import logging
import struct
import sys

from argparse import ArgumentParser

from radio.xbee import XBee

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class TestRadio(XBee):
    def on_message_received(self, remote_address, data):
        number, = struct.unpack('i', data)
        print(number)
        self.send(remote_address, struct.pack('i', number + 1))


def main():
    parser = ArgumentParser()
    parser.add_argument('--device', required=True)
    parser.add_argument('--init', action='store_true')
    args = parser.parse_args()

    xbee = TestRadio(args.device)

    xbee.open()

    if args.init:
        xbee.send_broadcast(struct.pack('i', 0))

    input()

    xbee.close()


if __name__ == '__main__':
    main()
