from multiprocessing import Lock

from protocol.request import Request


# TODO: check failed requests
class Container:
	def __init__(self):
		self._map = {}
		self.lock = Lock()

	def append(self, request_id: int, success, failure=None):
		if request_id in self._map:
			raise Exception("Request has already been sent!")

		self.lock.acquire()
		self._map[request_id] = Request(success, failure)
		self.lock.release()

	def touch(self, request_id: int):
		if request_id not in self._map:
			raise Exception("Request has not been sent!")

		self.lock.acquire()
		request = self._map[request_id].touch()
		self.lock.release()

		return request

	def remove(self, request_id: int):
		if request_id not in self._map:
			raise Exception("Request has not been sent!")

		self.lock.acquire()
		request = self._map.pop(request_id)
		self.lock.release()

		return request

	def removeByCondition(self, condition):
		self.lock.acquire()
		for request_id in self._map.keys():
			if condition(self._map[request_id]):
				self._map.pop(request_id)
		self.lock.release()

	def iterate(self, action):
		self.lock.acquire()
		for request_id in self._map.keys():
			action(self._map[request_id])
		self.lock.release()
