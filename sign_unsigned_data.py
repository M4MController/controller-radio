import asyncio
import json
import logging
import sys
from argparse import ArgumentParser

from sqlalchemy import (
    Column,
    LargeBinary,
    Integer,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from radio.xbee import XBee
from protocol.protocol import Protocol
from sign import Signature, Signifier

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

Base = declarative_base()


class SensorData(Base):
    __tablename__ = 'sensor_data'

    id = Column(Integer, primary_key=True)
    data = Column(JSON, nullable=False)
    sign = Column(LargeBinary)
    signer = Column(LargeBinary)


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


def get_unsigned_data(session):
    return session.query(SensorData).filter(SensorData.sign == None).filter(SensorData.signer == None).all()


def save_signed_data(session, data: SensorData, signature: Signature):
    logging.info('Sign received: %s %s', data.id, signature.sign)
    session.query(SensorData).filter_by(id=data.id).update({'sign': signature.sign, 'signer': signature.public_key})


async def main():
    parser = ArgumentParser()
    parser.add_argument('--device', required=True)
    parser.add_argument('--db-uri', required=True)

    args = parser.parse_args()

    xbee = XBee(args.device, baud_rate=9600)
    xbee.open()
    protocol = Protocol(xbee)

    device = await protocol.discover_first_remote_device()
    if device is None:
        raise Exception('no devices found')

    logging.info('Device found: %s', device)

    session = Session(create_engine(args.db_uri))

    all_unsigned_sensor_data = get_unsigned_data(session)
    logging.info('%d unsigned data', len(all_unsigned_sensor_data))
    for unsigned_sensor_data in all_unsigned_sensor_data:
        try:
            logging.info("Signing %d (%s)", unsigned_sensor_data.id, unsigned_sensor_data.data['timestamp'])
            unsigned_data = bytearray()
            unsigned_data.extend(map(ord, json.dumps(unsigned_sensor_data.data)))

            sign = await sign_data(protocol, unsigned_data, device)
            save_signed_data(session, unsigned_sensor_data, sign)

            session.commit()
            logging.info("Signed %d (%s)", unsigned_sensor_data.id, unsigned_sensor_data.data['timestamp'])
        except Exception as e:
            logging.error('error %s', e)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
