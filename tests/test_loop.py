# -*- coding: utf-8 -*-
"""
Unit tests for LoopedPipeline.

Tests cover:
- Loops until stopped
- Stop signals exit
- Calls inner pipeline start
"""
import unittest
from serial_to_mqtt.domain.pipeline import Pipeline
from serial_to_mqtt.domain.loop import LoopedPipeline


class CountingPipeline(Pipeline):
    """
    Pipeline that counts start calls and stops parent after limit.

    CountingPipeline increments counter on each start() call
    and stops the parent looped pipeline when limit is reached.

    Example usage:
        looped = LoopedPipeline(None)
        counting = CountingPipeline(looped, 5)
        looped._pipeline = counting
        looped.start()
        count = counting.count()  # Returns: 5
    """

    def __init__(self, parent, limit):
        """
        Create a CountingPipeline with parent and limit.

        Args:
            parent: LoopedPipeline to stop when limit reached
            limit (int): Number of iterations before stopping
        """
        self._parent = parent
        self._limit = limit
        self._count = 0

    def start(self):
        """
        Increment counter and stop parent if limit reached.
        """
        self._count = self._count + 1
        if self._count >= self._limit:
            self._parent.stop()

    def stop(self):
        """
        No-op for counting pipeline.
        """
        pass

    def count(self):
        """
        Return the number of start calls.

        Returns:
            int: Number of times start was called
        """
        return self._count


class SelfStoppingPipeline(Pipeline):
    """
    Pipeline that stops its parent on first call.

    SelfStoppingPipeline calls stop() on parent immediately
    when start() is called.

    Example usage:
        looped = LoopedPipeline(None)
        stopper = SelfStoppingPipeline(looped)
        looped._pipeline = stopper
        looped.start()  # Exits immediately
    """

    def __init__(self, parent):
        """
        Create a SelfStoppingPipeline with parent.

        Args:
            parent: LoopedPipeline to stop
        """
        self._parent = parent
        self._called = False

    def start(self):
        """
        Mark as called and stop parent.
        """
        self._called = True
        self._parent.stop()

    def stop(self):
        """
        No-op for self-stopping pipeline.
        """
        pass

    def called(self):
        """
        Return whether start was called.

        Returns:
            bool: True if start was called
        """
        return self._called


class LoopedPipelineLoopsUntilStopped(unittest.TestCase):
    """
    Tests that LoopedPipeline loops until stopped.
    """

    def test(self):
        """
        LoopedPipeline calls inner start multiple times until stopped.
        """
        looped = LoopedPipeline(CountingPipeline(LoopedPipeline(None), 1))
        counting = CountingPipeline(looped, 5)
        looped._pipeline = counting
        looped.start()
        self.assertEqual(
            5,
            counting.count(),
            "LoopedPipeline did not loop expected number of times"
        )


class LoopedPipelineStopSignalsExit(unittest.TestCase):
    """
    Tests that LoopedPipeline stop signals loop exit.
    """

    def test(self):
        """
        LoopedPipeline exits loop when stop is called.
        """
        looped = LoopedPipeline(SelfStoppingPipeline(None))
        stopper = SelfStoppingPipeline(looped)
        looped._pipeline = stopper
        looped.start()
        self.assertTrue(
            stopper.called(),
            "LoopedPipeline did not call inner pipeline before exiting"
        )


class LoopedPipelineCallsInnerStart(unittest.TestCase):
    """
    Tests that LoopedPipeline calls inner pipeline start.
    """

    def test(self):
        """
        LoopedPipeline calls inner pipeline start method.
        """
        looped = LoopedPipeline(None)
        counting = CountingPipeline(looped, 1)
        looped._pipeline = counting
        looped.start()
        self.assertGreater(
            counting.count(), 0,
            "LoopedPipeline did not call inner pipeline start"
        )


class LoopedPipelineStopBeforeStartIsNoop(unittest.TestCase):
    """
    Tests that LoopedPipeline stop before start is no-op.
    """

    def test(self):
        """
        LoopedPipeline stop before start does not raise error.
        """
        looped = LoopedPipeline(None)
        stopper = SelfStoppingPipeline(looped)
        looped._pipeline = stopper
        looped.stop()
        self.assertFalse(
            stopper.called(),
            "LoopedPipeline stop before start had unexpected effect"
        )


if __name__ == '__main__':
    unittest.main()
