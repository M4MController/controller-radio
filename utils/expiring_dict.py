import asyncio
from collections import namedtuple
from threading import Lock

ExpiringDictMeta = namedtuple("Meta", ["expiring_task", "on_delete"])

loop = asyncio.get_event_loop()


class ExpiringDict:
    def __init__(self, default_ttl=30, on_delete=None):
        self.__data = {}
        self.__meta = {}
        self.__default_ttl = default_ttl
        self.__on_delete = on_delete
        self.__lock = Lock()

    def set(self, key, value, ttl=None, on_delete=None):
        self.__set_with_expire(key, value, ttl, on_delete)

    def get(self, key, default=None):
        if key in self.__data or default is None:
            return self.__data[key]
        else:
            if key not in self.__data:
                return default
            else:
                return self.__data[key]

    def pop(self, key, default=None):
        if key in self.__data:
            result = self.__data[key]
            self.__delete_by_request(key)
            return result
        else:
            if default is None:
                return self.__data[key]
            else:
                return default

    def __delete_by_expire(self, key):
        self.__lock.acquire()
        if key in self.__meta:
            meta = self.__meta.pop(key)
            if meta.on_delete:
                try:
                    meta.on_delete()
                except ExpiringDict:
                    pass

        if self.__on_delete:
            if self.__on_delete:
                try:
                    self.__on_delete(key, self.__data[key])
                except ExpiringDict:
                    pass

        if key in self.__data:
            del self.__data[key]

        self.__lock.release()

    def __delete_by_request(self, key):
        self.__lock.acquire()

        meta = self.__meta.pop(key)
        meta.expiring_task.cancel()
        del self.__data[key]

        self.__lock.release()

    def __setitem__(self, key, value):
        self.__set_with_expire(key, value, self.__default_ttl)

    def __set_with_expire(self, key, value, ttl: float = None, on_delete=None):
        if not ttl:
            ttl = self.__default_ttl

        expiring_task = loop.call_later(ttl, lambda: self.__delete_by_expire(key))

        self.__lock.acquire()
        self.__meta[key] = ExpiringDictMeta(expiring_task=expiring_task, on_delete=on_delete)
        self.__data[key] = value
        self.__lock.release()

    def __delitem__(self, key):
        self.__delete_by_request(key)

    def __getitem__(self, key):
        return self.__data[key]

    def __iter__(self):
        return iter(self.__data)

    def __len__(self):
        return len(self.__data)
