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


def sign_data(protocol: Protocol, data: bytearray):
    sign = Signature(b'signifier public key', b'sign')  # todo: stub

    if Signifier.verify(data, sign):
        return sign
    else:
        raise Exception('sign verification failed')


def get_unsigned_data(session):
    return session.query(SensorData).filter(SensorData.sign == None).filter(SensorData.signer == None).all()


def save_signed_data(session, data: SensorData, signature: Signature):
    session.query(SensorData).filter_by(id=data.id).update({'sign': signature.sign, 'signer': signature.public_key})


def main():
    parser = ArgumentParser()
    parser.add_argument('--device', required=True)
    parser.add_argument('--db-uri', required=True)

    args = parser.parse_args()

    xbee = XBee(args.device)
    protocol = Protocol(xbee)

    session = Session(create_engine(args.db_uri))

    all_unsigned_sensor_data = get_unsigned_data(session)
    logging.info('%d unsigned data', len(all_unsigned_sensor_data))
    for unsigned_sensor_data in all_unsigned_sensor_data:
        unsigned_data = bytearray()
        unsigned_data.extend(map(ord, json.dumps(unsigned_sensor_data.data)))

        sign = sign_data(protocol, unsigned_data)
        save_signed_data(session, unsigned_sensor_data, sign)

        session.commit()
        logging.info("Signed %d (%s)", unsigned_sensor_data.id, unsigned_sensor_data.data['timestamp'])


if __name__ == '__main__':
    main()
