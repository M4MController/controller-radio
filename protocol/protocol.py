import struct
import typing

from sign import Signifier
from radio.xbee import XBee

data_type = typing.Union[bytearray, bytes]


class Vector:
	def __init__(self, lon: float, lat: float):
		self.lon = float(lon)
		self.lat = float(lat)


class Protocol:
	COMMAND_INTRODUCE = 1
	COMMAND_REQUEST_SIGN = 2
	COMMAND_RESPONSE_SIGN = 3

	def __init__(self, radio: XBee):
		self._radio = radio
		self._signifier = Signifier('public_key.pem', 'private_key.pem')

	# GPS - tuple, containing (lon, lat) where lon and lat - 8-byte doubles
	# Velocity - tuple, containing two 8-byte coordinate components
	def introduce_self(self, gps: Vector, velocity: Vector):
		data = bytearray()

		data.append(self.COMMAND_INTRODUCE)
		data.extend(struct.pack('f', gps.lon))
		data.extend(struct.pack('f', gps.lat))
		data.extend(struct.pack('f', velocity.lon))
		data.extend(struct.pack('f', velocity.lat))

		self._radio.send_broadcast(data)

	# Called when someone within range tells his current info
	def on_introduce_received(self, remote_address: bytearray, gps: Vector, vel: Vector):
		print('Remote address: ', remote_address)
		print('Gps: lon = ', gps.lon, '; lat = ', gps.lat)
		print('Velocity: lon = ', vel.lon, '; lat = ', vel.lat)

		self.sign_request(remote_address, bytes([1]))

	# Send data to sign to node with receiver_mac
	# receiver_mac should be bytearray of size 6
	# Data should be bytearray or bytes
	def sign_request(self, receiver_mac: data_type, data: data_type):
		data_container = bytearray()

		data_container.append(self.COMMAND_REQUEST_SIGN)
		data_container.extend(struct.pack('i', 42))
		data_container.extend(struct.pack('i', len(data)))
		data_container.extend(data)

		self._radio.send(receiver_mac, data_container)

	# Called on someone requests for his data to be signed
	def on_sign_request_received(self, remote_address, request_id: int, data: data_type):
		sign = self._signifier.sign(data)

		data_container = bytearray()

		data_container.append(self.COMMAND_RESPONSE_SIGN)
		data_container.extend(struct.pack('i', 42))
		data_container.extend(sign.public_key)
		data_container.extend(sign.sign)

		self._radio.send(remote_address, data)

	def on_message_received(self, remote_address: bytearray, data: bytearray):
		command = data[0]

		if command == self.COMMAND_INTRODUCE:
			gps = Vector(0, 0)
			gps.lon, = struct.unpack('f', data[1:5])
			gps.lat, = struct.unpack('f', data[5:9])

			vel = Vector(0, 0)
			vel.lon, = struct.unpack('f', data[9:13])
			vel.lat, = struct.unpack('f', data[13:17])

			self.on_introduce_received(remote_address, gps, vel)

			return

		if command == self.COMMAND_REQUEST_SIGN:
			request_id, = struct.unpack('i', data[1: 5])
			size, = struct.unpack('i', data[5:9])
			data_for_sign = data[9:9 + size]

			self.on_sign_request_received(remote_address, request_id, data_for_sign)

			return

	def on_unknown_command_received(self, remote_address: bytearray, data: bytearray):
		pass
