import logging
import sys

from argparse import ArgumentParser

from radio.xbee import XBee
from protocol.protocol import Protocol, Vector

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def main():
    parser = ArgumentParser()
    parser.add_argument('--device', required=True)
    parser.add_argument('--init', action='store_true')
    args = parser.parse_args()

    xbee = XBee(args.device)
    xbee.open()

    protocol = Protocol(xbee)

    if args.init:
        protocol.introduce_self(Vector(10, 10), Vector(15, 0))

    input()

    xbee.close()


if __name__ == '__main__':
    main()
