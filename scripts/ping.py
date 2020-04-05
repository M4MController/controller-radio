import asyncio
import logging
import sys
import time

from argparse import ArgumentParser
from random import randint

from protocol.commands import EchoRequest, EchoResponse
from protocol.protocol import Protocol
from radio.xbee import XBee

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
)

logger = logging.getLogger(__name__)


def generate_payload(len):
    return bytearray([randint(0, 255) for _ in range(len)])


async def main():
    parser = ArgumentParser()
    parser.add_argument("--device", required=True)
    parser.add_argument("--init", action="store_true")

    args = parser.parse_args()

    xbee = XBee(args.device, baud_rate=9600)
    xbee.open()
    device = await xbee.discover_first_remote_device()

    protocol = Protocol(xbee)
    protocol.on_request(EchoRequest, lambda _, request: EchoResponse(data=request.data))

    if args.init:
        while True:
            t = time.time()
            data = generate_payload(64)
            try:
                response = await protocol.send_request(device, EchoRequest(data=data))
                if response.data != data:
                    raise Exception("Check failed")
            except Exception as e:
                logger.error("Ping error %s: %s", device, e)
            else:
                logger.info("Ping %s: %s second(s)", device, time.time() - t)
    else:
        input()

    xbee.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
