from random import randint

from device_selector import Device
from device_selector.gvector import GVector
from utils.serializer import BaseModel


class BasePacket(BaseModel):
    ID: int = None

    fields = {
        "id": "byte",
    }

    def __init__(self, **kwargs):
        super().__init__(id=kwargs.pop("id", self.ID), **kwargs)


class BaseCommandPacket(BasePacket):
    ID: int = None  # == 1 or 2, see below this class
    COMMAND_ID: int = None

    fields = {
        **BasePacket.fields,
        "command_id": "byte",
        "request_id": "byte",
    }

    def __init__(self, **kwargs):
        super().__init__(
            command_id=kwargs.pop("command_id", self.COMMAND_ID),
            request_id=kwargs.pop("request_id", randint(0, 256)),
            **kwargs,
        )


class BaseRequestPacket(BaseCommandPacket):
    ID = 1


class BaseResponsePacket(BaseCommandPacket):
    ID = 2


class PingPongPacket(BasePacket):
    ID = 3

    fields = {
        **BasePacket.fields,
        "index": int,
        "payload": bytearray,
    }


class CurrentLocationPacket(BasePacket):
    ID = 4

    class Vector(BaseModel):
        fields = {
            "latitude": float,
            "longitude": float,
            "altitude": float,
        }

        @classmethod
        def create_from_gvector(cls, vector: GVector):
            return cls(latitude=vector.latitude, longitude=vector.longitude, altitude=vector.altitude)

        def to_gvector(self) -> GVector:
            return GVector(latitude=self.latitude, longitude=self.longitude, altitude=self.altitude)

    fields = {
        **BasePacket.fields,
        "position": Vector,
        "velocity": Vector
    }

    @classmethod
    def create_from_device(cls, device: Device):
        return cls(
            position=cls.Vector.create_from_gvector(device.position),
            velocity=cls.Vector.create_from_gvector(device.velocity),
        )

    def to_device(self) -> Device:
        return Device(position=self.position.to_gvector(), velocity=self.velocity.to_gvector())