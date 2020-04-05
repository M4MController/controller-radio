from .packets import BaseRequestPacket, BaseResponsePacket


class EchoResponse(BaseResponsePacket):
    COMMAND_ID = 1

    fields = {
        **BaseRequestPacket.fields,
        "data": bytearray,
    }


class EchoRequest(BaseRequestPacket):
    COMMAND_ID = 1
    response_class = EchoResponse

    fields = {
        **BaseRequestPacket.fields,
        "data": bytearray,
    }


class SignDataResponse(BaseResponsePacket):
    COMMAND_ID = 2

    fields = {
        **BaseRequestPacket.fields,
        "public_key": bytearray,
        "sign": bytearray,
    }


class SignDataRequest(BaseRequestPacket):
    COMMAND_ID = 2
    response_class = SignDataResponse

    fields = {
        **BaseRequestPacket.fields,
        "data": bytearray,
    }
