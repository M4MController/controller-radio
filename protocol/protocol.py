import struct
import typing

from sign import Signifier
from radio.xbee import XBee

data_type = typing.Union[bytearray, bytes]


class Vector:
	def __init__(self, lon: float, lat: float):
		self.lon = float(lon)
		self.lat = float(lat)


class Protocol(XBee):
	COMMAND_INTRODUCE = 1
	COMMAND_REQUEST_SIGN = 2
	COMMAND_RESPONSE_SIGN = 3

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
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

		self.send_broadcast(data)

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

		self.send(receiver_mac, data_container)

	# Called on someone requests for his data to be signed
	def on_sign_request_received(self, remote_address, request_id: int, data: data_type):
		sign = self._signifier.sign(data)

		data_container = bytearray()

		data_container.append(self.COMMAND_RESPONSE_SIGN)
		data_container.extend(struct.pack('i', request_id))
		data_container.extend(struct.pack('i', len(sign.public_key)))
		data_container.extend(sign.public_key)
		data_container.extend(struct.pack('i', len(sign.sign)))
		data_container.extend(sign.sign)

		self.send(remote_address, data)

	# Called when signed data is received
	def on_signed_data_received(self, request_id, key, signature):
		print('Request id: ', request_id)
		print('key: ', key)
		print('signature: ', signature)

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

		if command == self.COMMAND_RESPONSE_SIGN:
			request_id, = struct.unpack('i', data[1:5])
			key_size, = struct.unpack('i', data[5:9])
			key_right_index = 9 + key_size
			signature_size_right_index = 4 + key_right_index
			key = data[9:key_right_index]
			signature_size, = struct.unpack('i', data[key_right_index:signature_size_right_index])
			signature = data[signature_size_right_index:signature_size_right_index + signature_size]

			self.on_signed_data_received(request_id, key, signature)

			return




	def on_unknown_command_received(self, remote_address: bytearray, data: bytearray):
		pass
