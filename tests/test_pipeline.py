# -*- coding: utf-8 -*-
"""
Unit tests for SensorPipeline.

Tests cover:
- Publishing on successful read
- Logging on failed read
- Skipping non-publishable readings
- Stop is no-op
"""
import unittest
from serial_to_mqtt.result.either import Right, Left
from serial_to_mqtt.domain.pipeline import SensorPipeline


class FakeReading(object):
    """
    Fake reading that returns fixed publishable status.

    FakeReading allows tests to control whether a reading
    is considered publishable.

    Example usage:
        reading = FakeReading(True)
        reading.publishable()  # Returns: True
    """

    def __init__(self, status):
        """
        Create a FakeReading with publishable status.

        Args:
            status (bool): Whether reading is publishable
        """
        self._status = status

    def publishable(self):
        """
        Return whether this reading is publishable.

        Returns:
            bool: The configured publishable status
        """
        return self._status


class FakeSensor(object):
    """
    Fake sensor that returns predefined result.

    FakeSensor returns a fixed result from read(),
    useful for testing pipeline behavior.

    Example usage:
        sensor = FakeSensor(Right(FakeReading(True)))
        result = sensor.read()  # Returns the predefined result
    """

    def __init__(self, result):
        """
        Create a FakeSensor with predefined result.

        Args:
            result: Either to return from read()
        """
        self._result = result

    def read(self):
        """
        Return the predefined result.

        Returns:
            Either: The configured result
        """
        return self._result


class FakePublisher(object):
    """
    Fake publisher that records publications.

    FakePublisher counts how many times publish() was called,
    useful for verifying pipeline behavior.

    Example usage:
        publisher = FakePublisher()
        publisher.publish(reading)
        count = publisher.count()  # Returns: 1
    """

    def __init__(self):
        """
        Create a FakePublisher.
        """
        self._count = 0

    def publish(self, reading):
        """
        Record that publish was called.

        Args:
            reading: The reading to publish

        Returns:
            Either: Right indicating success
        """
        self._count = self._count + 1
        return Right("published")

    def count(self):
        """
        Return the number of publish calls.

        Returns:
            int: Number of times publish was called
        """
        return self._count


class FakeConfig(object):
    """
    Fake config that returns fixed port.

    FakeConfig provides a port number for error messages.

    Example usage:
        config = FakeConfig(3)
        port = config.port()  # Returns: 3
    """

    def __init__(self, port):
        """
        Create a FakeConfig with port number.

        Args:
            port (int): The port number
        """
        self._port = port

    def port(self):
        """
        Return the configured port number.

        Returns:
            int: The port number
        """
        return self._port


class FakeConsole(object):
    """
    Fake console that records messages.

    FakeConsole stores all messages passed to say(),
    useful for verifying error logging.

    Example usage:
        console = FakeConsole()
        console.say("Error occurred")
        messages = console.messages()  # Returns: ["Error occurred"]
    """

    def __init__(self):
        """
        Create a FakeConsole.
        """
        self._messages = []

    def say(self, message):
        """
        Record the message.

        Args:
            message (str): Message to record
        """
        self._messages.append(message)

    def messages(self):
        """
        Return all recorded messages.

        Returns:
            list: List of recorded messages
        """
        return self._messages


class SensorPipelinePublishesOnSuccess(unittest.TestCase):
    """
    Tests that SensorPipeline publishes when read succeeds.
    """

    def test(self):
        """
        SensorPipeline publishes when sensor read succeeds.
        """
        sensor = FakeSensor(Right(FakeReading(True)))
        publisher = FakePublisher()
        config = FakeConfig(3)
        console = FakeConsole()
        pipeline = SensorPipeline(sensor, publisher, config, console)
        pipeline.start()
        self.assertEqual(
            1,
            publisher.count(),
            "Pipeline did not publish on successful read"
        )


class SensorPipelineLogsOnFailure(unittest.TestCase):
    """
    Tests that SensorPipeline logs when read fails.
    """

    def test(self):
        """
        SensorPipeline logs error when sensor read fails.
        """
        sensor = FakeSensor(Left("Connection lost"))
        publisher = FakePublisher()
        config = FakeConfig(3)
        console = FakeConsole()
        pipeline = SensorPipeline(sensor, publisher, config, console)
        pipeline.start()
        self.assertEqual(
            1,
            len(console.messages()),
            "Pipeline did not log error on failed read"
        )


class SensorPipelineErrorMessageContainsPort(unittest.TestCase):
    """
    Tests that SensorPipeline error message contains port.
    """

    def test(self):
        """
        SensorPipeline error message includes COM port number.
        """
        sensor = FakeSensor(Left("Timeout"))
        publisher = FakePublisher()
        config = FakeConfig(7)
        console = FakeConsole()
        pipeline = SensorPipeline(sensor, publisher, config, console)
        pipeline.start()
        self.assertIn(
            "COM7",
            console.messages()[0],
            "Error message did not contain port number"
        )


class SensorPipelineSkipsNonPublishable(unittest.TestCase):
    """
    Tests that SensorPipeline skips non-publishable readings.
    """

    def test(self):
        """
        SensorPipeline does not publish non-publishable readings.
        """
        sensor = FakeSensor(Right(FakeReading(False)))
        publisher = FakePublisher()
        config = FakeConfig(3)
        console = FakeConsole()
        pipeline = SensorPipeline(sensor, publisher, config, console)
        pipeline.start()
        self.assertEqual(
            0,
            publisher.count(),
            "Pipeline published non-publishable reading"
        )


class SensorPipelineDoesNotLogOnSuccess(unittest.TestCase):
    """
    Tests that SensorPipeline does not log on success.
    """

    def test(self):
        """
        SensorPipeline does not log when read succeeds.
        """
        sensor = FakeSensor(Right(FakeReading(True)))
        publisher = FakePublisher()
        config = FakeConfig(3)
        console = FakeConsole()
        pipeline = SensorPipeline(sensor, publisher, config, console)
        pipeline.start()
        self.assertEqual(
            0,
            len(console.messages()),
            "Pipeline logged message on successful read"
        )


class SensorPipelineDoesNotPublishOnFailure(unittest.TestCase):
    """
    Tests that SensorPipeline does not publish on failure.
    """

    def test(self):
        """
        SensorPipeline does not publish when read fails.
        """
        sensor = FakeSensor(Left("Error"))
        publisher = FakePublisher()
        config = FakeConfig(3)
        console = FakeConsole()
        pipeline = SensorPipeline(sensor, publisher, config, console)
        pipeline.start()
        self.assertEqual(
            0,
            publisher.count(),
            "Pipeline published when read failed"
        )


class SensorPipelineStopIsNoop(unittest.TestCase):
    """
    Tests that SensorPipeline stop does nothing.
    """

    def test(self):
        """
        SensorPipeline stop completes without error.
        """
        sensor = FakeSensor(Right(FakeReading(True)))
        publisher = FakePublisher()
        config = FakeConfig(3)
        console = FakeConsole()
        pipeline = SensorPipeline(sensor, publisher, config, console)
        pipeline.stop()
        self.assertEqual(
            0,
            publisher.count(),
            "Pipeline stop had unexpected side effect"
        )


if __name__ == '__main__':
    unittest.main()
