# -*- coding: utf-8 -*-
"""
Asynchronous decorator for pipelines.

This module provides AsyncPipeline which runs any Pipeline
in a dedicated thread for non-blocking execution.

Example usage:
    looped = LoopedPipeline(SensorPipeline(...))
    async_pipeline = AsyncPipeline(looped)
    async_pipeline.start()  # Non-blocking, runs in thread

    # ... later ...
    async_pipeline.stop()   # Blocks until thread finishes
"""
import threading
from serial_to_mqtt.domain.pipeline import Pipeline


class AsyncPipeline(Pipeline):
    """
    Pipeline decorator that runs in a dedicated thread.

    AsyncPipeline wraps any Pipeline and runs its start()
    method in a separate thread for non-blocking execution.

    Example usage:
        looped = LoopedPipeline(SensorPipeline(...))
        async_pipeline = AsyncPipeline(looped)

        async_pipeline.start()  # Non-blocking
        # ... do other work ...
        async_pipeline.stop()   # Blocks until thread finishes
    """

    def __init__(self, pipeline):
        """
        Create an AsyncPipeline wrapping inner pipeline.

        Args:
            pipeline: Pipeline to run in thread
        """
        self._pipeline = pipeline
        self._thread = None

    def start(self):
        """
        Start inner pipeline in dedicated thread.

        Creates and starts a new thread that calls inner
        pipeline start(). Returns immediately.
        """
        self._thread = threading.Thread(target=self._pipeline.start)
        self._thread.start()

    def stop(self):
        """
        Stop inner pipeline and wait for thread.

        Calls inner pipeline stop() and blocks until
        the thread finishes execution.
        """
        self._pipeline.stop()
        if self._thread is not None:
            self._thread.join()
