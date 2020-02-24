import json

from sqlalchemy import (
    Column,
    LargeBinary,
    Integer,
)

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSON

Base = declarative_base()


class SensorData(Base):
    __tablename__ = 'sensor_data'

    id = Column(Integer, primary_key=True)
    data = Column(JSON, nullable=False)
    sign = Column(LargeBinary)
    signer = Column(LargeBinary)

    def get_data_for_sign(self) -> bytearray:
        unsigned_data = bytearray()
        unsigned_data.extend(map(ord, json.dumps(self.data)))
        return unsigned_data
