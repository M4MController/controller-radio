import asyncio
import logging
import os
import sys

from argparse import ArgumentParser

from database import Database
from protocol.commands import SignDataRequest, SignDataResponse
from protocol.protocol import Protocol, data_type
from radio.xbee import XBee
from sign import Signature, Signifier
from utils.concurrency import set_interval

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
)

logger = logging.getLogger(__name__)

use_stubs = bool(os.environ.get("USE_STUBS", False))

if not use_stubs:
    signifier = Signifier.from_files("public_key.pem", "private_key.pem")


def sign_data_handler(remote_address: data_type, request: SignDataRequest):
    sign = signifier.sign(request.data)
    return SignDataResponse(public_key=sign.public_key, sign=sign.sign)


async def sign_data_task(protocol, database):
    unsigned_data = database.get_unsigned_data()

    if not use_stubs:
        device = await protocol.radio.discover_first_remote_device()
        if device is None:
            logging.info("No devices nearby")
            return
        logging.info("Nearby device found: %s", device)

        for data in unsigned_data:
            sign_response = await protocol.send_request(
                device,
                SignDataRequest(data=data.get_data_for_sign()),
            )
            database.set_sign(data, Signature(public_key=sign_response.public_key, sign=sign_response.sign))
    else:
        for data in unsigned_data:
            sign = signifier.sign(data.get_data_for_sign())
            database.set_sign(data, sign)
            await asyncio.sleep(1)


async def main():
    parser = ArgumentParser()
    parser.add_argument('--device', required=True)
    parser.add_argument('--db-uri', required=False)
    parser.add_argument('--timeout', type=float, default=30)

    use_stubs = bool(os.environ.get('USE_STUBS', False))

    args = parser.parse_args()

    if not use_stubs:
        xbee = XBee(args.device)
        xbee.open()

        protocol = Protocol(xbee, args.timeout)
        protocol.on_request(SignDataRequest, sign_data_handler)

        if args.db_uri:
            database = Database(args.db_uri)

            set_interval(sign_data_task, 1, protocol, database)


if __name__ == "__main__":
    asyncio.async(main())
    loop = asyncio.get_event_loop()
    loop.run_forever()
