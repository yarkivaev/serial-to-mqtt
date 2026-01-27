# -*- coding: utf-8 -*-
"""
MQTT payload formatting.

This module provides the Formatter implementation for converting readings into
MQTT message payloads.

Example usage:
    formatter = Formatter()
    reading = TemperatureReading(epoch, celsius)
    payload = formatter.format(reading)  # Returns: {"ts": ..., "value": ...}
"""


class Formatter(object):
    """
    JSON formatter for readings.

    Formatter converts readings into JSON format matching the heater
    project requirements: {"ts": timestamp, "value": temperature}
    This serves as both the base class for domain-specific formatters
    and the default implementation when no domain-specific formatter is needed.

    Example usage:
        formatter = Formatter()
        reading = TemperatureReading(Epoch(1234567890000), Celsius(25.5))
        json_str = formatter.format(reading)
        # Returns: {"ts": 1234567890000, "value": 25.5}
    """

    def __init__(self):
        """
        Create a Formatter.
        """
        pass

    def format(self, reading):
        """
        Format a reading into JSON string.

        Args:
            reading (Reading): The reading to format

        Returns:
            str: JSON string with ts and value fields

        Delegates to the reading's json() method which already provides
        the correct format.
        """
        return reading.json()
