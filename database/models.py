import json

from sqlalchemy import (
    Column,
    LargeBinary,
    Integer, String,
)

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSON

SENSOR_TYPE_GPS = 6

Base = declarative_base()


class Sensor(Base):
    __tablename__ = "sensors"
    id = Column(String, primary_key=True)
    sensor_type = Column(Integer)


class SensorData(Base):
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True)
    data = Column(JSON, nullable=False)
    sign = Column(LargeBinary)
    signer = Column(LargeBinary)
    sensor_id = Column(String, nullable=False)

    def get_data_for_sign(self) -> bytearray:
        unsigned_data = bytearray()
        unsigned_data.extend(map(ord, json.dumps(self.data)))
        return unsigned_data
