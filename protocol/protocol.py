import asyncio
import logging
import typing

from radio.xbee import XBee
from utils.expiring_dict import ExpiringDict

from .packets import BasePacket, BaseRequestPacket, BaseResponsePacket

logger = logging.getLogger(__name__)

data_type = typing.Union[bytearray, bytes]
loop = asyncio.get_event_loop()


def request_uuid(address: data_type, request: BaseRequestPacket):
    return request.command_id << 8 + request.request_id  # todo: add address


class Protocol:
    def __init__(self, radio: XBee, timeout: float = 30):
        radio.on_message_received = self._packet_handler

        self._radio = radio
        self._expiring_dict = ExpiringDict(default_ttl=timeout)
        self._packet_subscriptions = {}
        self._command_handlers = {}

        self.on_packet(BaseRequestPacket, self._request_handler)
        self.on_packet(BaseResponsePacket, self._response_handler)

    @property
    def radio(self):
        return self._radio

    def send_packet(self, remote_address: data_type, packet: BasePacket):
        """
        Sends a single packet to a remote device, does not wait for response.
        """
        self._radio.send(remote_address, packet.serialize())

    def send_packet_broadcast(self, packet: BasePacket):
        """
        Sends a single packet to all devices, does not wait for response.
        """
        self._radio.send_broadcast(packet.serialize())

    def on_packet(self, packet_type: type, success):
        """
        Registers a callback on single packet received.
        """
        if issubclass(packet_type, BasePacket):
            self._packet_subscriptions[packet_type.ID] = (packet_type, success)
        else:
            raise Exception("event must be a subclass of BaseEvent")

    def _packet_handler(self, remote_address: data_type, data: bytearray):
        """
        Handler calls when single packed received by remote device.
        """
        packet = BasePacket.deserialize(data)
        logger.info("Packet received. remote_address=%s id=%s", remote_address, packet.id)
        if packet.id in self._packet_subscriptions:
            request_class, callback = self._packet_subscriptions[packet.id]
            callback(remote_address, request_class.deserialize(data))

    async def send_request(self, remote_address: data_type, request: BaseRequestPacket, timeout=None):
        """
        Sends a request to remote device, waits for response and returns it.
        """
        future = asyncio.Future()

        def callback(address: data_type, response: BaseResponsePacket):
            loop.call_soon_threadsafe(future.set_result, request.response_class.deserialize(response.raw_bytes))

        def failure():
            loop.call_soon_threadsafe(future.set_exception, Exception("Data transfer failed by timeout"))

        self._expiring_dict.set(request_uuid(remote_address, request), callback, on_delete=failure, ttl=timeout)

        logger.info(
            "Request sent: remote_address=%s command_id=%s request_id=%s",
            remote_address,
            request.command_id,
            request.request_id,
        )
        self.send_packet(remote_address, request)

        return await future

    def on_request(self, request_type: type, handler):
        """
        Registers a request handler.
        """
        if issubclass(request_type, BaseRequestPacket):
            def h(remote_address: data_type, request: BaseRequestPacket):
                response = handler(remote_address, request_type.deserialize(request.raw_bytes))

                if not isinstance(response, BaseResponsePacket):
                    raise Exception("response must be an instance of BaseResponsePacket")

                response.request_id = request.request_id
                logger.info(
                    "Response sent. remote_address=%s command_id=%s request_id=%s",
                    remote_address,
                    response.command_id,
                    response.request_id,
                )
                self.send_packet(remote_address, response)

            self._command_handlers[request_type.COMMAND_ID] = h
        else:
            raise Exception("event must be a subclass of BaseRequestPacket")

    def _request_handler(self, remote_address: data_type, request: BaseRequestPacket):
        """
        Handler calls when request received from remote device.
        """
        logger.info(
            "Request received. remote_address=%s command_id=%s request_id=%s",
            remote_address,
            request.command_id,
            request.request_id,
        )
        if request.command_id in self._command_handlers:
            internal_handler = self._command_handlers[request.command_id]
            internal_handler(remote_address, request)
        else:
            logging.error("No handler")

    def _response_handler(self, remote_address: data_type, response: BaseResponsePacket):
        """
        Handler called when response received from remote device.
        """
        logger.info(
            "Response received. remote_address=%s command_id=%s request_id=%s",
            remote_address,
            response.command_id,
            response.request_id,
        )

        callback = self._expiring_dict.pop(request_uuid(remote_address, response), None)
        if callback is not None:
            callback(remote_address, response)
        else:
            logger.error("No callback")
