# -*- coding: utf-8 -*-
"""
Message abstraction for protocol parsing.

This module provides interfaces for protocol messages that can be validated
and parsed into sensor readings.

Example usage:
    message = KsumMessage("!1;25.5;38444;")
    position = message.position()  # Returns: "1"
    value = message.value()  # Returns: "25.5"
    checksum = message.checksum()  # Returns: "38444"
"""


class Message(object):
    """
    Interface for protocol message implementations.

    Message represents a parsed protocol message with position, value, and
    checksum components. It provides access to each part of the message.
    """

    def position(self):
        """
        Extract the position field from the message.

        Returns:
            str: The position identifier
        """
        raise NotImplementedError("Subclasses must implement position")

    def value(self):
        """
        Extract the value field from the message.

        Returns:
            str: The measurement value as string
        """
        raise NotImplementedError("Subclasses must implement value")

    def checksum(self):
        """
        Extract the checksum field from the message.

        Returns:
            str: The checksum value as string
        """
        raise NotImplementedError("Subclasses must implement checksum")

    def payload(self):
        """
        Extract the payload that should be checksummed.

        Returns:
            str: The message portion used for checksum calculation
        """
        raise NotImplementedError("Subclasses must implement payload")
