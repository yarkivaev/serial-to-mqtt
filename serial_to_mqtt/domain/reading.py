# -*- coding: utf-8 -*-
"""
Sensor reading domain abstractions.

This module provides implementations for sensor readings,
including temperature, pressure, and humidity measurements with timestamps.

Example usage:
    from serial_to_mqtt.domain.measurement import Measurement
    from serial_to_mqtt.domain.unit import Unit
    timestamp = Epoch(1234567890000)
    unit = Unit("celsius", "°C")
    measurement = Measurement(unit, 25.5)
    reading = Reading(timestamp, measurement)
    json_str = reading.json()  # Returns: {"ts": 1234567890000, "value": 25.5}
"""
import json
import time


class Reading(object):
    """
    Generic reading implementation.

    Reading can represent any timestamped measurement without knowing
    the measurement type. This serves as both the base class for domain-specific
    readings and the default implementation when no domain-specific reading
    type is needed.

    Example usage:
        from serial_to_mqtt.domain.measurement import Measurement
        from serial_to_mqtt.domain.unit import Unit
        epoch = Epoch(1234567890000)
        unit = Unit("celsius", "°C")
        measurement = Measurement(unit, 25.5)
        reading = Reading(epoch, measurement)
        print(reading.json())  # {"ts": 1234567890000, "value": 25.5}
        measurement_obj = reading.measurement()
        value = measurement_obj.value()  # 25.5
    """

    def __init__(self, epoch, measurement):
        """
        Create a reading with timestamp and measurement.

        Args:
            epoch (Epoch): The timestamp when measurement was taken
            measurement (Measurement): The measurement object
        """
        self._epoch = epoch
        self._measurement = measurement

    def json(self):
        """
        Convert this reading to JSON string representation.

        Returns:
            str: JSON string with ts (timestamp) and value (measurement)
        """
        return json.dumps({
            "ts": self._epoch.milliseconds(),
            "value": self._measurement.value()
        })

    def measurement(self):
        """
        Extract the measurement from this reading.

        Returns:
            Measurement: The measurement object
        """
        return self._measurement


class Epoch(object):
    """
    Timestamp in milliseconds since Unix epoch.

    Epoch is a value object representing a point in time as milliseconds
    since January 1, 1970 UTC. This format matches MQTT message requirements.

    Example usage:
        clock = Clock()
        epoch = clock.epoch()
        ts = epoch.milliseconds()  # Returns: current time in milliseconds
    """

    def __init__(self, milliseconds):
        """
        Create an Epoch timestamp.

        Args:
            milliseconds (int): Milliseconds since Unix epoch
        """
        self._milliseconds = milliseconds

    def milliseconds(self):
        """
        Extract the numeric timestamp value.

        Returns:
            int: Milliseconds since Unix epoch
        """
        return self._milliseconds


class Clock(object):
    """
    Clock that provides current time as Epoch.

    Clock encapsulates the concept of "current time" and allows dependency
    injection for testability. Use Clock instead of static methods to get
    the current timestamp.

    Example usage:
        clock = Clock()
        epoch = clock.epoch()  # Returns: Epoch with current time
        ts = epoch.milliseconds()  # Returns: current time in milliseconds
    """

    def __init__(self):
        """
        Create a Clock.
        """
        pass

    def epoch(self):
        """
        Get current time as Epoch.

        Returns:
            Epoch: Current timestamp in milliseconds
        """
        return Epoch(int(time.time() * 1000))
