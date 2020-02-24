import asyncio
import logging
import os
import sys
import time

from threading import Timer

from argparse import ArgumentParser

from database import Database
from radio.xbee import XBee
from protocol.protocol import Protocol
from sign import Signature, Signifier

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


async def sign_data(protocol: Protocol, data: bytearray, device: bytearray):
    future = asyncio.Future()
    loop = asyncio.get_event_loop()

    def callback(public_key, sign):
        signature = Signature(public_key, sign)
        if Signifier.verify(data, signature):
            loop.call_soon_threadsafe(future.set_result, signature)
        else:
            loop.call_soon_threadsafe(future.set_exception, Exception('sign verification failed'))

    protocol.sign_request(device, data, callback)

    return await future


async def main():
    parser = ArgumentParser()
    parser.add_argument('--device', required=True)
    parser.add_argument('--db-uri', required=True)

    use_stubs = bool(os.environ.get('USE_STUBS', False))

    args = parser.parse_args()

    if not use_stubs:
        xbee = XBee(args.device)
        xbee.open()

        protocol = Protocol(xbee)
    else:
        signifier = Signifier.from_files('public_key.pem', 'private_key.pem')

    database = Database(args.db_uri)

    while True:
        unsigned_data = database.get_unsigned_data()

        if not use_stubs:
            device = await protocol.discover_first_remote_device()
            if device is None:
                logging.info('No devices nearby')
                continue
            logging.info('Nearby device found: %s', device)

        if not use_stubs:
            for data in unsigned_data:
                sign = await sign_data(protocol, data.get_data_for_sign(), device)
                database.set_sign(data, sign)
        else:
            for data in unsigned_data:
                sign = signifier.sign(data.get_data_for_sign())
                database.set_sign(data, sign)

    xbee.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
