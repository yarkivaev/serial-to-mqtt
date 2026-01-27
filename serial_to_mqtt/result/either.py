# -*- coding: utf-8 -*-
"""
Either monad for null-free error handling.

This module provides the Either abstraction for handling success and failure
cases without using null values. Either represents a value that can be one of
two types: Right (success) or Left (error).

Example usage:
    result = Right(42)
    if result.successful():
        print(result.value())  # Prints: 42

    error = Left("Something went wrong")
    if not error.successful():
        print(error.error())  # Prints: Something went wrong
"""


class Either(object):
    """
    Interface for Either monad representing success or failure.

    Either is an abstraction for values that can be in one of two states:
    successful (Right) or failed (Left). This eliminates the need for null
    values and provides type-safe error handling.
    """

    def successful(self):
        """
        Query whether this Either represents a successful result.

        Returns:
            bool: True if this is a Right (success), False if Left (error)
        """
        raise NotImplementedError("Subclasses must implement successful")

    def value(self):
        """
        Extract the successful value from this Either.

        Returns:
            object: The wrapped successful value

        Raises:
            RuntimeError: If this Either represents an error (Left)
        """
        raise NotImplementedError("Subclasses must implement value")

    def error(self):
        """
        Extract the error value from this Either.

        Returns:
            object: The wrapped error value

        Raises:
            RuntimeError: If this Either represents success (Right)
        """
        raise NotImplementedError("Subclasses must implement error")


class Right(Either):
    """
    Successful result in an Either monad.

    Right represents the success case of an Either. It encapsulates a
    successful value and provides access to it via the value() method.

    Example usage:
        success = Right({"temperature": 25.5})
        if success.successful():
            data = success.value()  # Returns {"temperature": 25.5}
    """

    def __init__(self, content):
        """
        Create a Right instance with successful value.

        Args:
            content: The successful value to wrap (must not be None)
        """
        self._content = content

    def successful(self):
        """
        Query whether this Either represents a successful result.

        Returns:
            bool: Always True for Right instances
        """
        return True

    def value(self):
        """
        Extract the successful value from this Either.

        Returns:
            object: The wrapped successful value
        """
        return self._content

    def error(self):
        """
        Extract the error value from this Either.

        Raises:
            RuntimeError: Always raises because Right contains success value
        """
        raise RuntimeError("Cannot extract error from successful Right")


class Left(Either):
    """
    Failed result in an Either monad.

    Left represents the error case of an Either. It encapsulates an error
    value and provides access to it via the error() method.

    Example usage:
        failure = Left("Connection timeout")
        if not failure.successful():
            message = failure.error()  # Returns "Connection timeout"
    """

    def __init__(self, problem):
        """
        Create a Left instance with error value.

        Args:
            problem: The error value to wrap (must not be None)
        """
        self._problem = problem

    def successful(self):
        """
        Query whether this Either represents a successful result.

        Returns:
            bool: Always False for Left instances
        """
        return False

    def value(self):
        """
        Extract the successful value from this Either.

        Raises:
            RuntimeError: Always raises because Left contains error value
        """
        raise RuntimeError("Cannot extract value from failed Left")

    def error(self):
        """
        Extract the error value from this Either.

        Returns:
            object: The wrapped error value
        """
        return self._problem
