from random import randint, random

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
