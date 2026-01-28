# -*- coding: utf-8 -*-
"""
Unit tests for Pipelines collection.

Tests cover:
- Starts all pipelines
- Stops all pipelines
- Empty collection is no-op
"""
import unittest
from serial_to_mqtt.domain.pipeline import Pipeline
from serial_to_mqtt.domain.pipelines import Pipelines


class RecordingPipeline(Pipeline):
    """
    Pipeline that records start and stop calls.

    RecordingPipeline tracks whether start() and stop()
    were called, useful for verifying collection behavior.

    Example usage:
        recording = RecordingPipeline()
        recording.start()
        started = recording.started()  # Returns: True
    """

    def __init__(self):
        """
        Create a RecordingPipeline.
        """
        self._started = False
        self._stopped = False

    def start(self):
        """
        Record that start was called.
        """
        self._started = True

    def stop(self):
        """
        Record that stop was called.
        """
        self._stopped = True

    def started(self):
        """
        Return whether start was called.

        Returns:
            bool: True if start was called
        """
        return self._started

    def stopped(self):
        """
        Return whether stop was called.

        Returns:
            bool: True if stop was called
        """
        return self._stopped


class PipelinesStartsFirstItem(unittest.TestCase):
    """
    Tests that Pipelines starts first item.
    """

    def test(self):
        """
        Pipelines start calls start on first item.
        """
        first = RecordingPipeline()
        second = RecordingPipeline()
        pipelines = Pipelines([first, second])
        pipelines.start()
        self.assertTrue(
            first.started(),
            "Pipelines did not start first item"
        )


class PipelinesStartsSecondItem(unittest.TestCase):
    """
    Tests that Pipelines starts second item.
    """

    def test(self):
        """
        Pipelines start calls start on second item.
        """
        first = RecordingPipeline()
        second = RecordingPipeline()
        pipelines = Pipelines([first, second])
        pipelines.start()
        self.assertTrue(
            second.started(),
            "Pipelines did not start second item"
        )


class PipelinesStopsFirstItem(unittest.TestCase):
    """
    Tests that Pipelines stops first item.
    """

    def test(self):
        """
        Pipelines stop calls stop on first item.
        """
        first = RecordingPipeline()
        second = RecordingPipeline()
        pipelines = Pipelines([first, second])
        pipelines.stop()
        self.assertTrue(
            first.stopped(),
            "Pipelines did not stop first item"
        )


class PipelinesStopsSecondItem(unittest.TestCase):
    """
    Tests that Pipelines stops second item.
    """

    def test(self):
        """
        Pipelines stop calls stop on second item.
        """
        first = RecordingPipeline()
        second = RecordingPipeline()
        pipelines = Pipelines([first, second])
        pipelines.stop()
        self.assertTrue(
            second.stopped(),
            "Pipelines did not stop second item"
        )


class PipelinesEmptyStartIsNoop(unittest.TestCase):
    """
    Tests that Pipelines empty start is no-op.
    """

    def test(self):
        """
        Pipelines start with empty list does not raise error.
        """
        pipelines = Pipelines([])
        pipelines.start()
        self.assertTrue(
            True,
            "Pipelines empty start raised unexpected error"
        )


class PipelinesEmptyStopIsNoop(unittest.TestCase):
    """
    Tests that Pipelines empty stop is no-op.
    """

    def test(self):
        """
        Pipelines stop with empty list does not raise error.
        """
        pipelines = Pipelines([])
        pipelines.stop()
        self.assertTrue(
            True,
            "Pipelines empty stop raised unexpected error"
        )


class PipelinesStartsAllThree(unittest.TestCase):
    """
    Tests that Pipelines starts all three items.
    """

    def test(self):
        """
        Pipelines start calls start on all three items.
        """
        items = [RecordingPipeline(), RecordingPipeline(), RecordingPipeline()]
        pipelines = Pipelines(items)
        pipelines.start()
        started = sum(1 for item in items if item.started())
        self.assertEqual(
            3,
            started,
            "Pipelines did not start all three items"
        )


class PipelinesStopsAllThree(unittest.TestCase):
    """
    Tests that Pipelines stops all three items.
    """

    def test(self):
        """
        Pipelines stop calls stop on all three items.
        """
        items = [RecordingPipeline(), RecordingPipeline(), RecordingPipeline()]
        pipelines = Pipelines(items)
        pipelines.stop()
        stopped = sum(1 for item in items if item.stopped())
        self.assertEqual(
            3,
            stopped,
            "Pipelines did not stop all three items"
        )


if __name__ == '__main__':
    unittest.main()
