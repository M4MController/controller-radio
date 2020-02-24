import asyncio


class Timer:
	def __init__(self, callback):
		self.callback = callback

	async def fire(self, interval: float, loop: bool = False):
		await asyncio.sleep(interval)
		self.callback()

		while loop:
			await asyncio.sleep(interval)
			self.callback()
