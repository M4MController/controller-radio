import asyncio
import logging
import threading

logger = logging.getLogger(__name__)


def start_thread(func, *args, **kwargs):
    def f(*args, **kwargs):
        if asyncio.iscoroutinefunction(func):
            loop = asyncio.new_event_loop()  # loop in a new thread
            loop.run_until_complete(func(*args, **kwargs))
        else:
            func(*args, **kwargs)

    thread = threading.Thread(target=f, *args, **kwargs)
    thread.start()
    return thread


def start_coroutine(func):
    loop = asyncio.get_event_loop()
    if asyncio.iscoroutinefunction(func):
        pass
    else:
        loop.call_soon_threadsafe(func)


def set_interval(func, interval, *args, **kwargs):
    if asyncio.iscoroutinefunction(func):
        async def main():
            while True:
                try:
                    await func(*args, **kwargs)
                except Exception as e:
                    logger.error("Error executing timeout callback: %e", e)
                await asyncio.sleep(interval)

    else:
        async def main():
            while True:
                try:
                    func(*args, **kwargs)
                except Exception as e:
                    logger.error("Error executing timeout callback: %e", e)
                await asyncio.sleep(interval)

    return asyncio.ensure_future(main())
