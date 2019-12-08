import time

from radio.xbee import XBee
from argparse import ArgumentParser

import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class TestRadio(XBee):
    def on_message_received(self, remote, data):
        logging.info(remote, ':', data)


def main():
    parser = ArgumentParser()
    parser.add_argument('--device', required=True)
    parser.add_argument('--read',  action='store_true')
    args = parser.parse_args()

    xbee = XBee(args.device)

    xbee.open()

    if not args.read:
        xbee.send_broadcast("hello!")
        xbee.send()

    i = 0
    while True:
        if not args.read:
            i += 1
            xbee.send_broadcast(str(i))
            logging.getLogger().info(str(i))
        time.sleep(1/3)

    xbee.close()


if __name__ == '__main__':
    main()
