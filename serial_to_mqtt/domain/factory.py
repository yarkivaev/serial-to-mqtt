# -*- coding: utf-8 -*-
"""
Factory abstractions for creating measurements and readings.

This module provides factory implementations that enable protocols to create
domain-specific measurements without knowing their concrete types.

Example usage:
    from serial_to_mqtt.domain.factory import MeasurementFactory
    from serial_to_mqtt.domain.factory import ReadingFactory
    from serial_to_mqtt.domain.reading import Clock

    measurement_factory = MeasurementFactory("celsius", "°C")
    reading_factory = ReadingFactory()

    measurement = measurement_factory.create(25.5)
    clock = Clock()
    epoch = clock.epoch()
    reading = reading_factory.create(epoch, measurement)
"""
from serial_to_mqtt.domain.measurement import Measurement
from serial_to_mqtt.domain.unit import Unit
from serial_to_mqtt.domain.reading import Reading


class MeasurementFactory(object):
    """
    Default factory for generic measurements.

    Creates Measurement objects with Unit. This serves as both the base class
    for domain-specific factories and the default implementation when no
    domain-specific factory is needed. This enables protocols to work
    with any sensor type without knowing the specific measurement domain.

    Example usage:
        factory = MeasurementFactory("celsius", "°C")
        measurement = factory.create(25.5)
        print(measurement.value())  # Prints: 25.5
        print(measurement.unit().name())  # Prints: celsius
    """

    def __init__(self, name, symbol):
        """
        Create a MeasurementFactory with unit specification.

        Args:
            name (str): The unit name (e.g., "celsius", "volt")
            symbol (str): The unit symbol (e.g., "°C", "V")
        """
        self._unit = Unit(name, symbol)

    def create(self, numeric):
        """
        Create a Measurement from numeric value.

        Args:
            numeric (float): The parsed numeric value

        Returns:
            Measurement: Generic measurement with the configured unit
        """
        return Measurement(self._unit, numeric)


class ReadingFactory(object):
    """
    Default factory for generic readings.

    Creates Reading objects. This serves as both the base class for
    domain-specific reading factories and the default implementation when no
    domain-specific reading factory is needed. This enables protocols to work
    with any sensor type without knowing the specific reading domain.

    Example usage:
        factory = ReadingFactory()
        measurement = Measurement(Unit("celsius", "°C"), 25.5)
        epoch = Epoch(1234567890000)
        reading = factory.create(epoch, measurement)
        print(reading.json())  # {"ts": 1234567890000, "value": 25.5}
    """

    def __init__(self):
        """
        Create a ReadingFactory.
        """
        pass

    def create(self, epoch, measurement):
        """
        Create a Reading from timestamp and measurement.

        Args:
            epoch (Epoch): The timestamp when measurement was taken
            measurement (Measurement): The measurement object

        Returns:
            Reading: Generic reading with timestamp and measurement
        """
        return Reading(epoch, measurement)
