# -*- coding: utf-8 -*-
"""
Checksum abstraction for protocol validation.

This module provides the Checksum interface for validating protocol messages
using different checksum algorithms (KSUM, CRC-16, etc.).

Example usage:
    checksum = KsumChecksum(calculator)
    message = KsumMessage("!1;25.5;38444;")
    is_valid = checksum.valid(message)  # Returns: True or False
"""


class Checksum(object):
    """
    Interface for checksum validation implementations.

    Checksum defines how to validate a message using a specific algorithm.
    Different implementations support different algorithms (KSUM, CRC-16, etc.).

    This abstraction enables the strategy pattern, allowing protocols to use
    different checksum algorithms.
    """

    def valid(self, message):
        """
        Validate a message using this checksum algorithm.

        Args:
            message (Message): The message to validate

        Returns:
            bool: True if checksum is valid, False otherwise
        """
        raise NotImplementedError("Subclasses must implement valid")
