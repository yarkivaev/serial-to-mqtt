# -*- coding: utf-8 -*-
"""
Unit abstractions for measurements.

Example usage:
    celsius = Unit("celsius", "°C")
    name = celsius.name()     # Returns: "celsius"
    symbol = celsius.symbol() # Returns: "°C"
"""


class Unit(object):
    """
    Generic unit implementation.

    Unit can represent any unit (celsius, pascal, percent, volt, etc.)
    without knowing its domain meaning. This serves as both the base class
    for domain-specific units and the default implementation when no
    domain-specific unit type is needed.

    Example usage:
        unit = Unit("celsius", "°C")
        print(unit.name())    # Prints: celsius
        print(unit.symbol())  # Prints: °C
    """

    def __init__(self, name, symbol):
        """
        Create a Unit with name and symbol.

        Args:
            name (str): The unit name (e.g., "celsius", "volt")
            symbol (str): The unit symbol (e.g., "°C", "V")
        """
        self._name = name
        self._symbol = symbol

    def name(self):
        """
        Extract the unit name.

        Returns:
            str: The unit name
        """
        return self._name

    def symbol(self):
        """
        Extract the unit symbol.

        Returns:
            str: The unit symbol
        """
        return self._symbol
