# -*- coding: utf-8 -*-
"""
Measurement abstractions for sensor readings.

Example usage:
    from serial_to_mqtt.domain.unit import Unit
    unit = Unit("celsius", "°C")
    measurement = Measurement(unit, 25.5)
    value = measurement.value()  # Returns: 25.5
    unit_name = measurement.unit().name()  # Returns: "celsius"
"""


class Measurement(object):
    """
    Generic measurement implementation.

    Measurement can represent any physical quantity (temperature,
    pressure, humidity, voltage, etc.) without knowing its domain meaning.
    This serves as both the base class for domain-specific measurements
    and the default implementation when no domain-specific type is needed.

    Example usage:
        from serial_to_mqtt.domain.unit import Unit
        unit = Unit("celsius", "°C")
        measurement = Measurement(unit, 25.5)
        value = measurement.value()  # Returns: 25.5
        unit_obj = measurement.unit()  # Returns: Unit instance
        unit_name = unit_obj.name()  # Returns: "celsius"
    """

    def __init__(self, unit, numeric):
        """
        Create a Measurement with unit and value.

        Args:
            unit (Unit): The measurement unit
            numeric (float): The measurement value
        """
        self._unit = unit
        self._numeric = numeric

    def value(self):
        """
        Extract the numeric measurement value.

        Returns:
            float: The measurement value
        """
        return self._numeric

    def unit(self):
        """
        Extract the measurement unit.

        Returns:
            Unit: The measurement unit
        """
        return self._unit
