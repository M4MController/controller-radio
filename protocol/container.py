from multiprocessing import Lock


# TODO: check failed requests
class Container:
	def __init__(self):
		self._map = {}
		self.lock = Lock()

	def append(self, request_id: int, callback):
		if request_id in self._map:
			raise Exception("Request has already been sent!")

		self.lock.acquire()
		self._map[request_id] = callback
		self.lock.release()

	def remove(self, request_id: int):
		if request_id not in self._map:
			raise Exception("Request has not been sent!")

		self.lock.acquire()
		callback = self._map.pop(request_id)
		self.lock.release()
		return callback
