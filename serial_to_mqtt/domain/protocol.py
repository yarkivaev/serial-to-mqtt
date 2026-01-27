# -*- coding: utf-8 -*-
"""
Protocol abstraction for parsing sensor messages.

This module provides the Protocol interface which enables strategy pattern
for different communication protocols (KSUM, Modbus RTU, etc.).

Example usage:
    protocol = KsumProtocol()
    result = protocol.parse(raw_bytes)
    if result.successful():
        reading = result.value()
        print(reading.json())
"""


class Protocol(object):
    """
    Interface for communication protocol implementations.

    Protocol defines how to parse raw bytes from a serial connection into
    Reading objects. Different implementations support different protocols
    (KSUM, Modbus RTU, etc.).
    """

    def parse(self, bytes):
        """
        Parse raw bytes into a Reading.

        Args:
            bytes: Raw bytes received from serial connection

        Returns:
            Either: Right(Reading) if parsing succeeds, Left(error) if fails
        """
        raise NotImplementedError("Subclasses must implement parse")
