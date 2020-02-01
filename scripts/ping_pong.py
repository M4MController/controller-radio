import asyncio
import logging
import sys

from argparse import ArgumentParser
from random import randint

from radio.xbee import XBee
from serializer import BaseModel


class Ball(BaseModel):
    fields = {
        'index': int,
        'payload': bytearray,
    }


def generate_payload(len):
    return bytearray([randint(0, 255) for _ in range(len)])


logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
)


class PingPong:
    def __init__(self, xbee: XBee):
        self._device = xbee
        self._device.on_message_received = self.on_message_received

    async def init(self):
        logging.info('init')
        address = await self._device.discover_first_remote_device()
        logging.info('address\t')
        self._device.send(address, Ball(index=0, payload=generate_payload(5)).serialize())

    def send(self, remote_address: bytearray, data: bytearray):
        ball = Ball.deserialize(data)
        ball.index += 1
        ball.payload = generate_payload(ball.index)
        try:
            self._device.send(remote_address, ball.serialize())
            logging.info("Send\t%s\t%d", remote_address, ball.index)
        except Exception as e:
            logging.error("Send error\t%s\t%s", remote_address, e)

    def on_message_received(self, remote_address: bytearray, data: bytearray):
        ball = Ball.deserialize(data)
        logging.info("Receive\t%s\t%d", remote_address, ball.index)
        ball.index += 1
        ball.payload = generate_payload(ball.index)
        try:
            self._device.send(remote_address, ball.serialize())
            logging.info("Send\t%s\t%d", remote_address, ball.index)
        except Exception as e:
            logging.error("Send error\t%s\t%s", remote_address, e)


async def main():
    parser = ArgumentParser()
    parser.add_argument('--device', required=True)
    parser.add_argument('--init', action='store_true')

    args = parser.parse_args()

    xbee = XBee(args.device, baud_rate=9600)
    xbee.open()

    ping_pong = PingPong(xbee)

    if args.init:
        await ping_pong.init()

    input()

    xbee.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
