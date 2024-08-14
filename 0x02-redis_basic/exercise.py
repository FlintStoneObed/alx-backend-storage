#!/usr/bin/env python3

import redis
import uuid
from typing import Union, Callable, Any
import functools

def count_calls(method: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator to count the number of times a method is called.

    This decorator uses Redis to keep track of the call count for the method.
    
    Args:
        method: The method to be decorated.

    Returns:
        A wrapped function that increments the call count and returns the result of the original method.
    """
    key = f"{method.__qualname__}:calls"

    @functools.wraps(method)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        """
        Increment the call count in Redis and return the result of the original method.
        
        Args:
            self: The instance of the class.
            *args: Positional arguments for the method.
            **kwargs: Keyword arguments for the method.

        Returns:
            The result of the original method.
        """
        self._redis.incr(key)
        return method(self, *args, **kwargs)

    return wrapper

def call_history(method: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator to record the history of calls to a method in Redis.

    This decorator stores the inputs and outputs of the method calls in Redis lists.
    
    Args:
        method: The method to be decorated.

    Returns:
        A wrapped function that logs input and output and returns the result of the original method.
    """
    input_key = f"{method.__qualname__}:inputs"
    output_key = f"{method.__qualname__}:outputs"

    @functools.wraps(method)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        """
        Store the input and output of the method call in Redis and return the result of the original method.
        
        Args:
            self: The instance of the class.
            *args: Positional arguments for the method.
            **kwargs: Keyword arguments for the method.

        Returns:
            The result of the original method.
        """
        self._redis.rpush(input_key, str(args))
        result = method(self, *args, **kwargs)
        self._redis.rpush(output_key, str(result))
        return result

    return wrapper

class Cache:
    """
    A Cache class for storing data in a Redis database with additional features such as call counting
    and call history recording.

    This class interacts with a Redis instance to store and retrieve data, and provides methods to
    count method calls and record the history of method inputs and outputs.
    """

    def __init__(self) -> None:
        """
        Initialize the Cache instance by creating a Redis client and flushing the database.
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store the given data in Redis with a randomly generated key.

        Args:
            data: The data to be stored in Redis. It can be a string, bytes, integer, or float.

        Returns:
            The key under which the data is stored in Redis.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Callable[[bytes], Any] = None) -> Union[str, int, float, None]:
        """
        Retrieve data from Redis and optionally convert it using a callable.

        Args:
            key: The key for the data to be retrieved from Redis.
            fn: An optional callable to convert the retrieved data to a different format.

        Returns:
            The data retrieved from Redis, converted using the callable if provided, otherwise as bytes.
        """
        data = self._redis.get(key)
        if data is None:
            return None
        if fn is not None:
            return fn(data)
        return data

    def get_str(self, key: str) -> str:
        """
        Retrieve data from Redis and convert it to a string.

        Args:
            key: The key for the data to be retrieved from Redis.

        Returns:
            The data retrieved from Redis, converted to a string.
        """
        return self.get(key, lambda x: x.decode('utf-8'))

    def get_int(self, key: str) -> int:
        """
        Retrieve data from Redis and convert it to an integer.

        Args:
            key: The key for the data to be retrieved from Redis.

        Returns:
            The data retrieved from Redis, converted to an integer.
        """
        return self.get(key, lambda x: int(x))

    def replay(self, method: Callable[..., Any]) -> None:
        """
        Display the history of calls for a particular method.

        Args:
            method: The method whose call history is to be displayed.
        """
        input_key = f"{method.__qualname__}:inputs"
        output_key = f"{method.__qualname__}:outputs"

        inputs = self._redis.lrange(input_key, 0, -1)
        outputs = self._redis.lrange(output_key, 0, -1)

        for i, (input_data, output_data) in enumerate(zip(inputs, outputs), 1):
            print(f"Call {i}:")
            print(f"    Inputs: {input_data.decode('utf-8')}")
            print(f"    Outputs: {output_data.decode('utf-8')}")

