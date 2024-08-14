#!/usr/bin/env python3

import requests
import cachetools

def get_page(url: str) -> str:
    """
    This function retrieves the HTML content of a given URL and caches the result for 10 seconds.
    
    Args:
    url (str): The URL to retrieve the HTML content from.
    
    Returns:
    str: The HTML content of the given URL.
    """
    
    # Create a cache with a TTL (time to live) of 10 seconds
    cache = cachetools.TTLCache(maxsize=100, ttl=10)
    
    # Check if the URL is already in the cache
    if url in cache:
        # If it is, return the cached result and increment the access count
        result = cache[url]
        cache[url] = result
        cache['count:{}'.format(url)] = cache.get('count:{}'.format(url), 0) + 1
        return result
else:
        # If not, retrieve the HTML content using requests
        result = requests.get(url).text
        
        # Cache the result and set the access count to 1
        cache[url] = result
        cache['count:{}'.format(url)] = 1
        
        # Return the HTML content
        return result

# Bonus: Implementing the use case with decorators

def cache_result(ttl=10):
 """
    This decorator caches the result of a function for a given TTL (time to live).
    
    Args:
    ttl (int): The time to live in seconds.
    
    Returns:
    function: The decorated function.
    """
    
    def decorator(function):
        cache = cachetools.TTLCache(maxsize=100, ttl=ttl)
        
        def wrapper(*args, **kwargs):
            key = str(args) + str(kwargs)
            if key in cache:
                return cache[key]
            else:
                result = function(*args, **kwargs)
                cache[key] = result
                return result
        
        return wrapper
    
    return decorator

@cache_result(ttl=10)
def get_page_with_decorator(url: str) -> str:
    """
    This function retrieves the HTML content of a given URL and caches the result for 10 seconds using a decorator.
    
    Args:
    url (str): The URL to retrieve the HTML content from.
    
    Returns:
    str: The HTML content of the given URL.
    """
    
    return requests.get(url).text
