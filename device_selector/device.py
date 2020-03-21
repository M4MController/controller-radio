from device_selector.gvector import GVector


class Device:
	def __init__(self, position: GVector, velocity: GVector, acceleration: GVector = GVector.nil()):
		self.position = position
		self.velocity = velocity
		self.acceleration = acceleration

	def __str__(self):
		return 'Position: {pos};\nVelocity: {vel};\nAcceleration: {acc};'\
			.format(pos=self.position, vel=self.velocity, acc=self.acceleration)

	def position_after(self, secs: float):
		return self.position + self.velocity * secs + self.acceleration * (secs ** 2) / 2

	def distance_to(self, other):
		return (other.position - self.position).length()

	def distance_to_after(self, other, secs: float):
		return (other.position_after(secs) - self.position_after(secs)).length()
