# -*- coding: utf-8 -*-
"""
Unit tests for measurement value objects.
"""

import unittest
from serial_to_mqtt.domain.measurement import Measurement
from serial_to_mqtt.domain.unit import Unit


class MeasurementTest(unittest.TestCase):
    """Tests for Measurement generic measurement value object."""

    def test_encapsulates_value(self):
        """Measurement encapsulates numeric value."""
        unit = Unit("celsius", "°C")
        measurement = Measurement(unit, 25.5)
        self.assertEqual(
            measurement.value(),
            25.5,
            "Measurement must return the encapsulated value"
        )

    def test_encapsulates_unit(self):
        """Measurement encapsulates unit."""
        unit = Unit("celsius", "°C")
        measurement = Measurement(unit, 25.5)
        self.assertEqual(
            measurement.unit().name(),
            "celsius",
            "Measurement must return the encapsulated unit"
        )

    def test_works_with_celsius_unit(self):
        """Measurement works with celsius unit."""
        unit = Unit("celsius", "°C")
        measurement = Measurement(unit, 20.0)
        self.assertEqual(
            measurement.unit().symbol(),
            "°C",
            "Measurement must work with celsius unit"
        )

    def test_works_with_volt_unit(self):
        """Measurement works with volt unit."""
        unit = Unit("volt", "V")
        measurement = Measurement(unit, 12.5)
        self.assertEqual(
            measurement.unit().symbol(),
            "V",
            "Measurement must work with volt unit"
        )

    def test_works_with_pascal_unit(self):
        """Measurement works with pascal unit."""
        unit = Unit("pascal", "Pa")
        measurement = Measurement(unit, 101325.0)
        self.assertEqual(
            measurement.unit().name(),
            "pascal",
            "Measurement must work with pascal unit"
        )

    def test_handles_negative_values(self):
        """Measurement handles negative values."""
        unit = Unit("celsius", "°C")
        measurement = Measurement(unit, -15.5)
        self.assertEqual(
            measurement.value(),
            -15.5,
            "Measurement must handle negative values"
        )

    def test_handles_zero_value(self):
        """Measurement handles zero value."""
        unit = Unit("celsius", "°C")
        measurement = Measurement(unit, 0.0)
        self.assertEqual(
            measurement.value(),
            0.0,
            "Measurement must handle zero value"
        )

    def test_handles_large_values(self):
        """Measurement handles large values."""
        unit = Unit("pascal", "Pa")
        measurement = Measurement(unit, 1000000.0)
        self.assertEqual(
            measurement.value(),
            1000000.0,
            "Measurement must handle large values"
        )

    def test_handles_precise_decimals(self):
        """Measurement handles precise decimal values."""
        unit = Unit("celsius", "°C")
        measurement = Measurement(unit, 25.123456789)
        self.assertEqual(
            measurement.value(),
            25.123456789,
            "Measurement must handle precise decimal values"
        )

    def test_value_is_immutable(self):
        """Measurement value is immutable."""
        unit = Unit("celsius", "°C")
        measurement = Measurement(unit, 25.5)
        original_value = measurement.value()
        _ = measurement.value()
        self.assertEqual(
            measurement.value(),
            original_value,
            "Measurement value must be immutable"
        )

    def test_unit_is_immutable(self):
        """Measurement unit is immutable."""
        unit = Unit("celsius", "°C")
        measurement = Measurement(unit, 25.5)
        original_unit = measurement.unit().name()
        _ = measurement.unit()
        self.assertEqual(
            measurement.unit().name(),
            original_unit,
            "Measurement unit must be immutable"
        )

    def test_works_with_percent_unit(self):
        """Measurement works with percent unit."""
        unit = Unit("percent", "%")
        measurement = Measurement(unit, 65.0)
        self.assertEqual(
            measurement.unit().symbol(),
            "%",
            "Measurement must work with percent unit"
        )

    def test_works_with_ampere_unit(self):
        """Measurement works with ampere unit."""
        unit = Unit("ampere", "A")
        measurement = Measurement(unit, 2.5)
        self.assertEqual(
            measurement.unit().name(),
            "ampere",
            "Measurement must work with ampere unit"
        )


if __name__ == "__main__":
    unittest.main()
