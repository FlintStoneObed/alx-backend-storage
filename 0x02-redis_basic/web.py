#!/usr/bin/env python3

import redis
import requests
from typing import Callable
import functools

# Create a Redis client
redis_client = redis.Redis()

def cache_with_expiration(expiration: int) -> Callable[[Callable[..., str]], Callable[..., str]]:
    """
    Decorator to cache the result of a function call with an expiration time in Redis.

    Args:
        expiration: The expiration time in seconds for the cache.

    Returns:
        A decorator that caches the result of the decorated function.
    """
    def decorator(func: Callable[..., str]) -> Callable[..., str]:
        @functools.wraps(func)
        def wrapper(url: str) -> str:
            key = f"cache:{url}"
            cached_result = redis_client.get(key)
            if cached_result:
                return cached_result.decode('utf-8')
            result = func(url)
            redis_client.setex(key, expiration, result)
            return result
        return wrapper
    return decorator

def count_accesses(func: Callable[..., str]) -> Callable[..., str]:
    """
    Decorator to count the number of times a URL is accessed.

    Args:
        func: The function to be decorated.

    Returns:
        A decorator that increments the access count for the URL in Redis.
    """
    @functools.wraps(func)
    def wrapper(url: str) -> str:
        count_key = f"count:{url}"
        redis_client.incr(count_key)
        return func(url)
    return wrapper

@cache_with_expiration(10)
@count_accesses
def get_page(url: str) -> str:
    """
    Fetches the HTML content of a given URL.

    This function uses the requests library to retrieve the HTML content of the specified URL. 
    It is decorated to cache the result for 10 seconds and track the number of accesses.

    Args:
        url: The URL to fetch.

    Returns:
        The HTML content of the URL as a string.
    """
    response = requests.get(url)
    response.raise_for_status()
    return response.text
