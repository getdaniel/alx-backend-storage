#!/usr/bin/env python3
""" Redis Basic."""
import redis
from typing import Callable, Union
from uuid import uuid4


class Cache:
    """ Implement cache strategy with Redis."""
    def __init__(self) -> None:
        """Initializes a Cache instance."""
        self._redis =  redis.Redis()
        self._redis.flushdb(True)

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """Generate a random key (e.g. using uuid), store the input data
           in Redis using the random key and return the key.
        """
        data_key = str(uuid4())
        self._redis.set(data_key, data)

        return data_key

    def get(self,
            key: str,
            fn: Callable = None) -> Union[str, bytes, int, float]:
        """ Retreive data from redis storage."""
        data = self._redis.get(key)

        return fn(data) if fn is not None else data

    def get_str(self, key: str) -> str:
        """ Retreive string data from redis storage."""
        return self.get(key, lambda d: d.decode('utf-8'))

    def get_int(self, key: str) -> int:
        """ Retreive integer data from redis storage.."""
        return self.get(key, lambda d: int(d))
