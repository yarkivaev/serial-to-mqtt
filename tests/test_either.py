# -*- coding: utf-8 -*-
"""
Unit tests for Either monad.

Tests follow CLAUDE.md principles:
- One assertion per test
- Test names are full English sentences
- No setUp/tearDown
- Tests close resources they use
- Each test prepares clean state
"""
import unittest
from serial_to_mqtt.result.either import Right, Left


class TestRight(unittest.TestCase):
    """Tests for Right (success case) implementation."""

    def test_right_successful_returns_true(self):
        """Right successful returns true."""
        result = Right(42)
        self.assertTrue(result.successful(), "Right should report successful as true")

    def test_right_value_returns_wrapped_value(self):
        """Right value returns wrapped value."""
        content = {"temperature": 25.5}
        result = Right(content)
        self.assertEqual(result.value(), content, "Right should return wrapped value")

    def test_right_error_raises_runtime_error(self):
        """Right error raises runtime error."""
        result = Right("success")
        with self.assertRaises(RuntimeError):
            result.error()

    def test_right_wraps_unicode_string(self):
        """Right wraps unicode string."""
        unicode_content = u"Температура: 25°C"
        result = Right(unicode_content)
        self.assertEqual(result.value(), unicode_content, "Right should wrap unicode content")


class TestLeft(unittest.TestCase):
    """Tests for Left (error case) implementation."""

    def test_left_successful_returns_false(self):
        """Left successful returns false."""
        result = Left("error occurred")
        self.assertFalse(result.successful(), "Left should report successful as false")

    def test_left_error_returns_wrapped_error(self):
        """Left error returns wrapped error."""
        problem = "Connection timeout"
        result = Left(problem)
        self.assertEqual(result.error(), problem, "Left should return wrapped error")

    def test_left_value_raises_runtime_error(self):
        """Left value raises runtime error."""
        result = Left("failure")
        with self.assertRaises(RuntimeError):
            result.value()

    def test_left_wraps_unicode_error_message(self):
        """Left wraps unicode error message."""
        unicode_error = u"Ошибка подключения к серверу"
        result = Left(unicode_error)
        self.assertEqual(result.error(), unicode_error, "Left should wrap unicode error")


if __name__ == '__main__':
    unittest.main()
