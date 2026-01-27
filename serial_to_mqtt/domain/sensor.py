# -*- coding: utf-8 -*-
"""
Sensor abstraction for reading temperature measurements.

This module provides the Sensor implementation which coordinates
serial connection and protocol parsing.

Example usage:
    connection = FramedConnection(delayed, delimiter)
    protocol = KsumProtocol()
    sensor = Sensor(connection, protocol)

    result = sensor.read()
    if result.successful():
        reading = result.value()
        print(reading.json())
"""
import time
from serial_to_mqtt.result.either import Right, Left


class Sensor(object):
    """
    Sensor implementation using connection and protocol.

    Sensor coordinates two collaborators:
    1. Connection - provides raw bytes from hardware
    2. Protocol - parses bytes into Reading

    Example usage:
        connection = FramedConnection(delayed, delimiter)
        protocol = KsumProtocol(...)
        sensor = Sensor(connection, protocol)

        result = sensor.read()
        if result.successful():
            print(result.value().json())
    """

    def __init__(self, connection, protocol):
        """
        Create a Sensor with connection and protocol.

        Args:
            connection: Connection providing complete messages
            protocol: Protocol for parsing bytes into Reading
        """
        self._connection = connection
        self._protocol = protocol

    def read(self):
        """
        Read a measurement from the sensor.

        Returns:
            Either: Right(Reading) if successful, Left(error) if failed
        """
        result = self._connection.receive()
        if not result.successful():
            return Left(result.error())
        return self._protocol.parse(result.value())


class Delay(object):
    """
    Configurable delay between sensor readings.

    Delay waits for a specified duration between sensor readings.

    Example usage:
        delay = Delay(0.3)
        delay.wait()  # Blocks for 0.3 seconds
    """

    def __init__(self, seconds):
        """
        Create a Delay with specified duration.

        Args:
            seconds (float): Duration to wait in seconds
        """
        self._seconds = seconds

    def wait(self):
        """
        Wait for the configured duration.

        This method blocks for the configured number of seconds.
        """
        time.sleep(self._seconds)
