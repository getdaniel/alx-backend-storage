#!/usr/bin/env python3
""" Redis Basic."""
from functools import wraps
import redis
from typing import Any, Callable, Union
from uuid import uuid4


def count_calls(method: Callable) -> Callable:
    """Implement a system to count how many times methods
       of the Cache class are called.
    """
    @wraps(method)
    def wrapper(self, *args, **kargs) -> Any:
        """ Implements counting functionality."""
        if isinstance(self._redis, redis.Redis):
            self._redis.incr(method.__qualname__)
        return method(self, *args, **kargs)

    return wrapper


def call_history(method: Callable) -> Callable:
    """ Implements a system call history"""
    @wraps(method)
    def wrapper(self, *args, **kargs) -> Any:
        """Implements call history functionality.."""
        in_key = '{}:inputs'.format(method.__qualname__)
        out_key = '{}:outputs'.format(method.__qualname__)
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(in_key, str(args))
        output = method(self, *args, **kargs)
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(out_key, output)
        return output

    return wrapper


def replay(fn: Callable) -> None:
    """ Display the history of calls."""
    if fn is None or not hasattr(fn, '__self__'):
        return
    redis_store = getattr(fn.__self__, '_redis', None)
    if not isinstance(redis_store, redis.Redis):
        return

    in_key = '{}:inputs'.format(fn.__qualname__)
    out_key = '{}:outputs'.format(fn.__qualname__)

    fxn_call_count = 0
    if redis_store.exists(fn.__qualname__) != 0:
        fxn_call_count = int(redis_store.get(fn.__qualname__))

    print('{} was called {} times:'.format(fn.__qualname__, fxn_call_count))
    fxn_inputs = redis_store.lrange(in_key, 0, -1)
    fxn_outputs = redis_store.lrange(out_key, 0, -1)
    for fxn_inputs, fxn_outputs in zip(fxn_inputs, fxn_outputs):
        print('{}(*{})'.format(
            fn.__qualname__,
            fxn_inputs.decode('utf-8'),
            fxn_outputs
        ))


class Cache:
    """ Implement cache strategy with Redis."""
    def __init__(self) -> None:
        """Initializes a Cache instance."""
        self._redis = redis.Redis()
        self._redis.flushdb(True)

    @count_calls
    @call_history
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
