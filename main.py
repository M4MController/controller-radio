import asyncio
import logging
import os
import sys

from argparse import ArgumentParser

from database import Database
from device_selector import Device, pick_available
from protocol.commands import SignDataRequest, SignDataResponse
from protocol.packets import CurrentLocationPacket
from protocol.protocol import Protocol, data_type
from radio.xbee import XBee
from sign import Signature, Signifier
from utils.concurrency import set_interval
from utils.expiring_dict import ExpiringDict

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
)

logger = logging.getLogger(__name__)

use_stubs = bool(os.environ.get("USE_STUBS", False))


signifier = Signifier.from_files("public_key.pem", "private_key.pem")


def sign_data_handler(remote_address: data_type, request: SignDataRequest):
    sign = signifier.sign(request.data)
    return SignDataResponse(public_key=sign.public_key, sign=sign.sign)


gps_cache = ExpiringDict(default_ttl=2)


class GpsDeviceWithAddress(Device):
    def __init__(self, address, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.address = address


def gps_data_received(remote_address: data_type, packet: CurrentLocationPacket):
    logging.info("GPS received: %s", packet)
    gps_cache.set(
        hash(str(remote_address)),
        GpsDeviceWithAddress(
            address=remote_address,
            position=packet.position.to_gvector(),
            velocity=packet.velocity.to_gvector()),
    )


async def sign_data_task(protocol, database):
    unsigned_data = database.get_unsigned_data()

    if not use_stubs:
        device = None
        logging.info("Devices with GPS info: %d", len(gps_cache))
        if len(gps_cache):
            me = database.get_latest_gps()
            devices = pick_available(me=me, others=gps_cache.values())
            logging.info("Devices available by GPS: %d", len(devices))
            if len(devices):
                logging.info("Device picked: %s", devices[0].address)

        if device is None:
            device = await protocol.radio.discover_first_remote_device()
            logging.info("Nearby device found: %s", device)

        if device is None:
            logging.info("No devices nearby")
            return

        for data in unsigned_data:
            sign_response = await protocol.send_request(
                device,
                SignDataRequest(data=data.get_data_for_sign()),
            )
            database.set_sign(data, Signature(public_key=sign_response.public_key, sign=sign_response.sign))
    else:
        for data in unsigned_data:
            sign = signifier.sign(data.get_data_for_sign())
            await asyncio.sleep(1)
            database.set_sign(data, sign)


async def send_gps_task(protocol, database):
    device_location = database.get_latest_gps()
    gps_packet = CurrentLocationPacket.create_from_device(device_location)
    logging.info("Send GPS: %s", gps_packet)
    protocol.send_packet_broadcast(gps_packet)


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
        protocol.on_packet(CurrentLocationPacket, gps_data_received)
        protocol.on_request(SignDataRequest, sign_data_handler)

        if args.db_uri:
            database = Database(args.db_uri)

            set_interval(sign_data_task, 1, protocol, database)
            set_interval(send_gps_task, 1, protocol, database)
    else:
        if args.db_uri:
            database = Database(args.db_uri)
            set_interval(sign_data_task, 1, None, database)


if __name__ == "__main__":
    asyncio.ensure_future(main())
    loop = asyncio.get_event_loop()
    loop.run_forever()
