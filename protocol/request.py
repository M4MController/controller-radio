from datetime import datetime


class Request:
	def __init__(self, success, failure=None):
		self.success = success
		self.failure = failure
		self.timestamp = datetime.now()

	def touch(self):
		self.timestamp = datetime.now()

		if self.failure is not None:
			self.failure()

		return self
