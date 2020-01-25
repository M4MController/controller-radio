import logging
import struct
import sys

from argparse import ArgumentParser

from radio.xbee import XBee
from protocol.protocol import Protocol, Vector, data_type

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def introduce_callback_factory(protocol: Protocol):
    def signed_callback(key: data_type, signature: data_type):
        print('Key: ', key)
        print('Signature: ', signature)

    def introduce_callback(remote_address: data_type, gps: Vector, velocity: Vector):
        print('Remote address: ', remote_address)
        print('Gps: ', gps)
        print('Velocity: ', velocity)

        protocol.sign_request(remote_address, struct.pack('i', 1), signed_callback)

    return introduce_callback


def main():
    parser = ArgumentParser()
    parser.add_argument('--device', required=True)
    parser.add_argument('--init', action='store_true')
    args = parser.parse_args()

    xbee = XBee(args.device)
    xbee.open()

    protocol = Protocol(xbee)
    protocol.introduce_subscribers(introduce_callback_factory(protocol))

    if args.init:
        protocol.introduce_self(Vector(10, 10), Vector(15, 0))

    input()

    xbee.close()


if __name__ == '__main__':
    main()
