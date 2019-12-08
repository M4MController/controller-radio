import struct
from radio.xbee import XBee


class Protocol(XBee):
	COMMAND_INTRODUCE = 1

	# GPS - tuple, containing (lon, lat) where lon and lat - 8-byte doubles
	# Velocity - tuple, containing two 8-byte coordinate components
	def introduce_self(self, gps, velocity):
		data = bytearray()

		data.append(self.COMMAND_INTRODUCE)
		data.extend(struct.pack('d', gps.lon))
		data.extend(struct.pack('d', gps.lat))
		data.extend(struct.pack('d', velocity.lon))
		data.extend(struct.pack('d', velocity.lat))

		self.send_broadcast(data)
