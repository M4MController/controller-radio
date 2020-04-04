import logging
import typing
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from device_selector.device import Device
from device_selector.gvector import GVector
from sign import Signature

from .models import Sensor, SensorData, SENSOR_TYPE_GPS

INTERVAL = 9
GPS_MAX_TIMEOUT = 2.5


class Database:
    def __init__(self, db_uri: str):
        self._session = Session(create_engine(db_uri))

    @property
    def _sensor_gps_id(self):
        if not hasattr(self, "__sensor_gps_id"):
            gpses = self._session.query(Sensor).filter(Sensor.sensor_type == SENSOR_TYPE_GPS).all()
            if len(gpses):
                self.__sensor_gps_id = gpses[0].id
        return self.__sensor_gps_id

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

    def get_latest_gps(self) -> typing.Optional[Device]:
        sensor_id = self._sensor_gps_id
        if not sensor_id:
            return None

        sensor_data = self._session.query(SensorData) \
            .filter(SensorData.sensor_id == sensor_id) \
            .order_by(SensorData.id.desc()) \
            .limit(2) \
            .all()
        if len(sensor_data) < 2:
            return None

        p1 = sensor_data[0].data
        p2 = sensor_data[1].data

        time1 = datetime.strptime(p1["timestamp"], "%Y-%m-%dT%H:%M:%S")
        time2 = datetime.strptime(p2["timestamp"], "%Y-%m-%dT%H:%M:%S")

        now = datetime.utcnow()
        if (now - time1).seconds > GPS_MAX_TIMEOUT or (now - time2).seconds > GPS_MAX_TIMEOUT:
            return None

        g1 = GVector(latitude=p1["value"]["lat"], longitude=p1["value"]["lon"], altitude=0)
        g2 = GVector(latitude=p2["value"]["lat"], longitude=p2["value"]["lon"], altitude=0)
        return Device(position=g1, velocity=GVector.create_from_two_points(g1, g2, time1 - time2))


__all__ = [
    'Database',
]
