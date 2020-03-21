from math import sqrt


class GVector:
	def __init__(self, latitude: float, longitude: float, altitude: float):
		self.latitude = latitude
		self.longitude = longitude
		self.altitude = altitude

	def __str__(self):
		return '(lat: {lat}; lon: {lon}; alt: {alt})'.format(lat=self.latitude, lon=self.longitude, alt=self.altitude)

	@classmethod
	def nil(cls):
		return GVector(0, 0, 0)

	def length(self):
		return sqrt(self.latitude**2 + self.longitude**2 + self.altitude**2)

	def distance_to(self, other):
		return (other - self).length()

	def __abs__(self):
		return self.length()

	def __add__(self, other):
		return GVector(self.latitude + other.latitude, self.longitude + other.longitude, self.altitude + other.altitude)

	def __sub__(self, other):
		return GVector(self.latitude - other.latitude, self.longitude - other.longitude, self.altitude - other.altitude)

	def __mul__(self, scalar: float):
		return GVector(self.latitude * scalar, self.longitude * scalar, self.altitude * scalar)

	def __truediv__(self, scalar: float):
		return GVector(self.latitude / scalar, self.longitude / scalar, self.altitude / scalar)

	def __iadd__(self, other):
		self.latitude += other.latitude
		self.longitude += other.longitude
		self.altitude += other.altitude

	def __isub__(self, other):
		self.latitude -= other.latitude
		self.longitude -= other.longitude
		self.altitude -= other.altitude

	def __imul__(self, scalar: float):
		self.latitude *= scalar
		self.longitude *= scalar
		self.altitude *= scalar

	def __idiv__(self, scalar):
		self.latitude /= scalar
		self.longitude /= scalar
		self.altitude /= scalar
