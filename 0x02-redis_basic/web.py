#!/usr/bin/env python3
""" Implementing an expiring web cache and tracker
    obtain the HTML content of a particular URL and returns it.
"""
import requests
import redis
import json
from functools import wraps

r = redis.Redis()

def cache(ex=10):
    """ Implement cach function."""
    def decorator(func):
        """" Implement the decoration functionality."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            """ Wrapper functinality."""
            url = args[0]
            # Check if the URL is already cached
            cached_response = r.get(url)
            if cached_response:
                # If the URL is cached, return the cached response
                print(f"Returning cached response for {url}")
                r.incr(f"count:{url}")
                return json.loads(cached_response)
            result = func(*args, **kwargs)
            r.set(url, json.dumps(result), ex=ex)
            r.incr(f"count:{url}")
            return result
        return wrapper
    return decorator

@cache(ex=10)
def get_page(url: str) -> str:
    """If the URL is not cached, send a request to the URL."""
    response = requests.get(url)
    return response.text


if __name__ == "__main__":
    get_page('http://slowwly.robertomurray.co.uk')
