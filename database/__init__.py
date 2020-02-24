import logging
import typing

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from sign import Signature
from .models import SensorData

INTERVAL = 9


class Database:
    def __init__(self, db_uri: str):
        self._session = Session(create_engine(db_uri))

    def get_unsigned_data(self, limit=10) -> typing.List[SensorData]:
        query_limit = limit * INTERVAL

        sensor_data = self._session.query(SensorData) \
                          .filter(SensorData.sign == None) \
                          .filter(SensorData.signer == None) \
                          .order_by(SensorData.id.desc()) \
                          .limit(query_limit) \
                          .all()[::INTERVAL]
        logging.info('%d unsigned data found', len(sensor_data))
        return sensor_data

    def set_sign(self, sensor_data: SensorData, signature: Signature):
        self._session.query(SensorData) \
            .filter_by(id=sensor_data.id) \
            .update(
            {'sign': signature.sign, 'signer': signature.public_key},
        )
        self._session.commit()
        logging.info('Sign saved for %d', sensor_data.id)


__all__ = [
    'Database',
]
