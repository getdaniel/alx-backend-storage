#!/usr/bin/env python3
""" Implement an expiring web cache and tracker."""
from functools import wraps
import redis
import requests
from typing import Callable


def page_counter(method: Callable) -> Callable:
    """ Count the call to request."""
    redi = redis.Redis()

    @wraps(method)
    def wrapper(urli) -> str:
        """ Implements the functionality of call requests."""
        redi.incr(f'count:{url}')
        expire_count = redi.get(f'cached:{url}')
        if expire_count:
            return expire_count.decode('utf-8')
        expire_count = method(url)
        redi.set(f'count:{url}', 0)
        redi.setex(f'cached:{url}', 10, expire_count)

        return expire_count

    return wrapper


@page_counter
def get_page(url: str) -> str:
    """ Impelements core function of get page which is accessed."""
    return requests.get(url).text
