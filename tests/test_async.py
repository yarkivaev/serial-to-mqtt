# -*- coding: utf-8 -*-
"""
Unit tests for AsyncPipeline.

Tests cover:
- Starts thread
- Stop blocks until done
- One pipeline continues when other blocks
"""
import unittest
import threading
import time
from serial_to_mqtt.domain.pipeline import Pipeline
from serial_to_mqtt.domain.loop import LoopedPipeline
from serial_to_mqtt.domain.async import AsyncPipeline


class MarkerPipeline(Pipeline):
    """
    Pipeline that marks an event when started.

    MarkerPipeline sets a threading Event when start()
    is called, useful for detecting thread execution.

    Example usage:
        event = threading.Event()
        marker = MarkerPipeline(event)
        marker.start()
        started = event.is_set()  # Returns: True
    """

    def __init__(self, event):
        """
        Create a MarkerPipeline with event.

        Args:
            event: threading.Event to set on start
        """
        self._event = event

    def start(self):
        """
        Set the event to mark execution.
        """
        self._event.set()

    def stop(self):
        """
        No-op for marker pipeline.
        """
        pass


class BlockingPipeline(Pipeline):
    """
    Pipeline that blocks until event is set.

    BlockingPipeline waits on a threading Event in start(),
    useful for simulating slow or hung connections.

    Example usage:
        release = threading.Event()
        blocking = BlockingPipeline(release)

        # In another thread: blocking.start()  # Blocks
        release.set()  # Unblocks the pipeline
    """

    def __init__(self, event):
        """
        Create a BlockingPipeline with release event.

        Args:
            event: threading.Event to wait on
        """
        self._event = event
        self._running = True

    def start(self):
        """
        Block until event is set.
        """
        self._event.wait()

    def stop(self):
        """
        Set event to release blocking wait.
        """
        self._event.set()
        self._running = False


class CounterPipeline(Pipeline):
    """
    Pipeline that counts executions with thread safety.

    CounterPipeline increments a counter on each start()
    using a lock for thread safety.

    Example usage:
        counter = CounterPipeline()
        counter.start()
        counter.start()
        count = counter.count()  # Returns: 2
    """

    def __init__(self):
        """
        Create a CounterPipeline.
        """
        self._count = 0
        self._lock = threading.Lock()
        self._running = True

    def start(self):
        """
        Increment counter with lock.
        """
        with self._lock:
            self._count = self._count + 1

    def stop(self):
        """
        Mark as stopped.
        """
        self._running = False

    def count(self):
        """
        Return the execution count.

        Returns:
            int: Number of times start was called
        """
        with self._lock:
            return self._count


class LoopingCounterPipeline(Pipeline):
    """
    Pipeline that loops counting until stopped.

    LoopingCounterPipeline loops in start(), incrementing
    counter each iteration until stop() is called.

    Example usage:
        counter = LoopingCounterPipeline()
        # In thread: counter.start()
        time.sleep(0.1)
        counter.stop()
        count = counter.count()  # Returns: iterations done
    """

    def __init__(self):
        """
        Create a LoopingCounterPipeline.
        """
        self._count = 0
        self._lock = threading.Lock()
        self._running = False

    def start(self):
        """
        Loop incrementing counter until stopped.
        """
        self._running = True
        while self._running:
            with self._lock:
                self._count = self._count + 1
            time.sleep(0.001)

    def stop(self):
        """
        Signal to stop looping.
        """
        self._running = False

    def count(self):
        """
        Return the execution count.

        Returns:
            int: Number of iterations completed
        """
        with self._lock:
            return self._count


class AsyncPipelineStartsThread(unittest.TestCase):
    """
    Tests that AsyncPipeline starts pipeline in thread.
    """

    def test(self):
        """
        AsyncPipeline starts inner pipeline in separate thread.
        """
        event = threading.Event()
        marker = MarkerPipeline(event)
        async_pipeline = AsyncPipeline(marker)
        async_pipeline.start()
        started = event.wait(timeout=1.0)
        async_pipeline.stop()
        self.assertTrue(
            started,
            "AsyncPipeline did not start inner pipeline in thread"
        )


class AsyncPipelineStopBlocksUntilDone(unittest.TestCase):
    """
    Tests that AsyncPipeline stop blocks until thread done.
    """

    def test(self):
        """
        AsyncPipeline stop waits for thread to complete.
        """
        event = threading.Event()
        blocking = BlockingPipeline(event)
        async_pipeline = AsyncPipeline(blocking)
        async_pipeline.start()
        async_pipeline.stop()
        self.assertTrue(
            event.is_set(),
            "AsyncPipeline stop did not release blocking pipeline"
        )


class AsyncPipelineRunsNonBlocking(unittest.TestCase):
    """
    Tests that AsyncPipeline start returns immediately.
    """

    def test(self):
        """
        AsyncPipeline start returns without blocking.
        """
        release = threading.Event()
        blocking = BlockingPipeline(release)
        async_pipeline = AsyncPipeline(blocking)
        returned = threading.Event()
        def starter():
            async_pipeline.start()
            returned.set()
        thread = threading.Thread(target=starter)
        thread.start()
        started = returned.wait(timeout=0.5)
        release.set()
        thread.join(timeout=1.0)
        async_pipeline.stop()
        self.assertTrue(
            started,
            "AsyncPipeline start blocked instead of returning immediately"
        )


class AsyncPipelineContinuesWhenOtherBlocks(unittest.TestCase):
    """
    Tests that fast pipeline continues when other blocks.
    """

    def test(self):
        """
        Fast async pipeline continues while other is blocked.
        """
        release = threading.Event()
        blocking = BlockingPipeline(release)
        counter = LoopingCounterPipeline()
        async1 = AsyncPipeline(blocking)
        async2 = AsyncPipeline(counter)
        async1.start()
        async2.start()
        time.sleep(0.05)
        count_while_blocked = counter.count()
        release.set()
        async1.stop()
        async2.stop()
        self.assertGreater(
            count_while_blocked, 0,
            "Fast pipeline did not continue while other was blocked"
        )


class AsyncPipelineStopWithoutStartIsNoop(unittest.TestCase):
    """
    Tests that AsyncPipeline stop without start is no-op.
    """

    def test(self):
        """
        AsyncPipeline stop before start does not raise error.
        """
        counter = CounterPipeline()
        async_pipeline = AsyncPipeline(counter)
        async_pipeline.stop()
        self.assertEqual(
            0,
            counter.count(),
            "AsyncPipeline stop without start had unexpected effect"
        )


if __name__ == '__main__':
    unittest.main()
