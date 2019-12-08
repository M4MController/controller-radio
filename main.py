import logging
import sys

from argparse import ArgumentParser

from protocol.protocol import Protocol, Vector

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

def main():
    parser = ArgumentParser()
    parser.add_argument('--device', required=True)
    parser.add_argument('--init', action='store_true')
    args = parser.parse_args()

    xbee = Protocol(args.device)

    xbee.open()

    if args.init:
        xbee.introduce_self(Vector(10, 10), Vector(15, 0))

    input()

    xbee.close()


if __name__ == '__main__':
    main()
