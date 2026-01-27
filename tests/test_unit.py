# -*- coding: utf-8 -*-
"""
Unit tests for unit value objects.
"""

import unittest
from serial_to_mqtt.domain.unit import Unit


class UnitTest(unittest.TestCase):
    """Tests for Unit generic unit value object."""

    def test_encapsulates_name(self):
        """Unit encapsulates name."""
        unit = Unit("celsius", "°C")
        self.assertEqual(
            unit.name(),
            "celsius",
            "Unit must return the encapsulated name"
        )

    def test_encapsulates_symbol(self):
        """Unit encapsulates symbol."""
        unit = Unit("celsius", "°C")
        self.assertEqual(
            unit.symbol(),
            "°C",
            "Unit must return the encapsulated symbol"
        )

    def test_works_with_celsius(self):
        """Unit works with celsius."""
        unit = Unit("celsius", "°C")
        self.assertEqual(
            unit.name(),
            "celsius",
            "Unit must work with celsius"
        )
        self.assertEqual(
            unit.symbol(),
            "°C",
            "Unit symbol must be °C"
        )

    def test_works_with_fahrenheit(self):
        """Unit works with fahrenheit."""
        unit = Unit("fahrenheit", "°F")
        self.assertEqual(
            unit.name(),
            "fahrenheit",
            "Unit must work with fahrenheit"
        )
        self.assertEqual(
            unit.symbol(),
            "°F",
            "Unit symbol must be °F"
        )

    def test_works_with_kelvin(self):
        """Unit works with kelvin."""
        unit = Unit("kelvin", "K")
        self.assertEqual(
            unit.name(),
            "kelvin",
            "Unit must work with kelvin"
        )
        self.assertEqual(
            unit.symbol(),
            "K",
            "Unit symbol must be K"
        )

    def test_works_with_pascal(self):
        """Unit works with pascal."""
        unit = Unit("pascal", "Pa")
        self.assertEqual(
            unit.name(),
            "pascal",
            "Unit must work with pascal"
        )
        self.assertEqual(
            unit.symbol(),
            "Pa",
            "Unit symbol must be Pa"
        )

    def test_works_with_bar(self):
        """Unit works with bar."""
        unit = Unit("bar", "bar")
        self.assertEqual(
            unit.name(),
            "bar",
            "Unit must work with bar"
        )
        self.assertEqual(
            unit.symbol(),
            "bar",
            "Unit symbol must be bar"
        )

    def test_works_with_percent(self):
        """Unit works with percent."""
        unit = Unit("percent", "%")
        self.assertEqual(
            unit.name(),
            "percent",
            "Unit must work with percent"
        )
        self.assertEqual(
            unit.symbol(),
            "%",
            "Unit symbol must be %"
        )

    def test_works_with_volt(self):
        """Unit works with volt."""
        unit = Unit("volt", "V")
        self.assertEqual(
            unit.name(),
            "volt",
            "Unit must work with volt"
        )
        self.assertEqual(
            unit.symbol(),
            "V",
            "Unit symbol must be V"
        )

    def test_works_with_ampere(self):
        """Unit works with ampere."""
        unit = Unit("ampere", "A")
        self.assertEqual(
            unit.name(),
            "ampere",
            "Unit must work with ampere"
        )
        self.assertEqual(
            unit.symbol(),
            "A",
            "Unit symbol must be A"
        )

    def test_name_is_immutable(self):
        """Unit name is immutable."""
        unit = Unit("celsius", "°C")
        original_name = unit.name()
        _ = unit.name()
        self.assertEqual(
            unit.name(),
            original_name,
            "Unit name must be immutable"
        )

    def test_symbol_is_immutable(self):
        """Unit symbol is immutable."""
        unit = Unit("celsius", "°C")
        original_symbol = unit.symbol()
        _ = unit.symbol()
        self.assertEqual(
            unit.symbol(),
            original_symbol,
            "Unit symbol must be immutable"
        )

    def test_handles_lowercase_names(self):
        """Unit handles lowercase names."""
        unit = Unit("celsius", "°C")
        self.assertTrue(
            unit.name().islower(),
            "Unit must handle lowercase names"
        )

    def test_symbol_is_not_empty(self):
        """Unit symbol is not empty."""
        unit = Unit("celsius", "°C")
        self.assertTrue(
            len(unit.symbol()) > 0,
            "Unit symbol must not be empty"
        )

    def test_name_is_not_empty(self):
        """Unit name is not empty."""
        unit = Unit("celsius", "°C")
        self.assertTrue(
            len(unit.name()) > 0,
            "Unit name must not be empty"
        )


if __name__ == "__main__":
    unittest.main()
