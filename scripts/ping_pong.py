import asyncio
import logging
import sys
import time

from argparse import ArgumentParser
from random import randint

from radio.xbee import XBee
from protocol.protocol import Protocol
from protocol.packets import PingPongPacket


def generate_payload(len):
    return bytearray([randint(0, 255) for _ in range(len)])


logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
)


class PingPongManager:
    def __init__(self, xbee: XBee):
        self._xbee = xbee
        self._protocol = Protocol(xbee)
        self._protocol.on_packet(PingPongPacket, self.on_message_received)
        self._time = time.time()

    async def init(self):
        logging.info('init')
        address = await self._xbee.discover_first_remote_device()
        logging.info('address\t')

        self._protocol.send_packet(address, PingPongPacket(index=0, payload=generate_payload(0)))

    def on_message_received(self, remote_address: bytearray, ping_pong: PingPongPacket):
        t = time.time()
        delta = t - self._time
        self._time = t

        logging.info("Received (%s) \t%s\t%d", delta, remote_address, ping_pong.index)
        ping_pong.index += 1
        ping_pong.payload = generate_payload(ping_pong.index)
        try:
            self._protocol.send_packet(remote_address, ping_pong)
            logging.info("Send\t%s\t%d", remote_address, ping_pong.index)
        except Exception as e:
            logging.error("Send error\t%s\t%s", remote_address, e)


async def main():
    parser = ArgumentParser()
    parser.add_argument('--device', required=True)
    parser.add_argument('--init', action='store_true')

    args = parser.parse_args()

    xbee = XBee(args.device, baud_rate=9600)
    xbee.open()

    ping_pong = PingPongManager(xbee)

    if args.init:
        await ping_pong.init()

    input()

    xbee.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
