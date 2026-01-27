# -*- coding: utf-8 -*-
"""
Sensor abstraction for reading temperature measurements.

This module provides the Sensor implementation which coordinates
serial connection, protocol parsing, and delay between readings.

Example usage:
    connection = SerialConnection(port, config)
    protocol = KsumProtocol()
    delay = Delay()
    sensor = Sensor(connection, protocol, delay)

    result = sensor.read()
    if result.successful():
        reading = result.value()
        print(reading.json())
"""
import time
from serial_to_mqtt.result.either import Right, Left


class Sensor(object):
    """
    Sensor implementation using serial connection and protocol.

    Sensor coordinates three collaborators:
    1. SerialConnection - provides raw bytes from hardware
    2. Protocol - parses bytes into Reading
    3. Delay - waits between readings

    This serves as both the base class for domain-specific sensors
    and the default implementation when no domain-specific sensor is needed.

    Example usage:
        connection = SerialConnection(13, SerialConfig())
        protocol = KsumProtocol()
        delay = Delay()
        sensor = Sensor(connection, protocol, delay)

        result = sensor.read()
        if result.successful():
            print(result.value().json())
    """

    def __init__(self, connection, protocol, delay):
        """
        Create a Sensor with connection, protocol, and delay.

        Args:
            connection: SerialConnection providing raw bytes
            protocol: Protocol for parsing bytes into Reading
            delay: Delay to wait between readings
        """
        self._connection = connection
        self._protocol = protocol
        self._delay = delay

    def read(self):
        """
        Read a temperature measurement from the sensor.

        Returns:
            Either: Right(Reading) if successful, Left(error) if failed

        This method:
        1. Waits for the delay period
        2. Receives bytes from the connection
        3. Parses bytes using the protocol
        4. Returns Either with Reading or error
        """
        self._delay.wait()
        bytes_result = self._connection.receive()
        if not bytes_result.successful():
            return Left(bytes_result.error())
        return self._protocol.parse(bytes_result.value())


class Delay(object):
    """
    One second delay implementation.

    Delay waits for one second between sensor readings.
    This matches the legacy system's polling interval.
    Serves as both the base class for domain-specific delays
    and the default implementation.

    Example usage:
        delay = Delay()
        delay.wait()  # Blocks for 1 second
    """

    def __init__(self):
        """
        Create a Delay.
        """
        pass

    def wait(self):
        """
        Wait for one second.

        This method blocks for 1 second before returning.
        """
        time.sleep(1)
