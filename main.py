import logging
import struct
import sys
import time

from argparse import ArgumentParser

from radio.xbee import XBee
from protocol.protocol import Protocol, Vector, data_type, EVENT_INTRODUCE, EVENT_ASK

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


def introduce_callback_factory(protocol: Protocol):
    def signed_callback(key: data_type, signature: data_type):
        print('Key: ', key)
        print('Signature: ', signature)

    def introduce_callback(remote_address: data_type, gps: Vector, velocity: Vector):
        print('Remote address: ', remote_address)
        print('Gps: ', gps)
        print('Velocity: ', velocity)

        protocol.sign_request(remote_address, struct.pack('i', 1), signed_callback)

    def ask_callback(request_id: int, remote_address: data_type):
        protocol.introduce_to(remote_address, Vector(0, 0), Vector(10, 10))

    return [introduce_callback, ask_callback]


def main():
    parser = ArgumentParser()
    parser.add_argument('--device', required=True)
    parser.add_argument('--init', action='store_true')
    args = parser.parse_args()

    xbee = XBee(args.device)
    xbee.open()

    protocol = Protocol(xbee)
    callbacks = introduce_callback_factory(protocol)
    protocol.event(EVENT_ASK, callbacks[1])

    while True:
        time.sleep(100)

    xbee.close()


if __name__ == '__main__':
    main()
