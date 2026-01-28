# -*- coding: utf-8 -*-
"""
Looping decorator for pipelines.

This module provides LoopedPipeline which wraps any Pipeline
and calls start() repeatedly until stop() is called.

Example usage:
    inner = SensorPipeline(sensor, publisher, config, console)
    looped = LoopedPipeline(inner)

    # In another thread: looped.stop()
    looped.start()  # Blocks, loops until stopped
"""
from serial_to_mqtt.domain.pipeline import Pipeline


class LoopedPipeline(Pipeline):
    """
    Pipeline decorator that loops until stopped.

    LoopedPipeline wraps any Pipeline and calls start()
    repeatedly in a loop until stop() is called.

    Example usage:
        inner = SensorPipeline(sensor, publisher, config, console)
        looped = LoopedPipeline(inner)

        # Start in background thread:
        thread = Thread(target=looped.start)
        thread.start()

        # Later, signal stop:
        looped.stop()
        thread.join()
    """

    def __init__(self, pipeline):
        """
        Create a LoopedPipeline wrapping inner pipeline.

        Args:
            pipeline: Pipeline to loop
        """
        self._pipeline = pipeline
        self._running = False

    def start(self):
        """
        Loop inner pipeline until stopped.

        This method blocks, calling inner pipeline start()
        repeatedly until stop() sets running flag to False.
        """
        self._running = True
        while self._running:
            self._pipeline.start()

    def stop(self):
        """
        Signal to stop looping.

        Sets running flag to False, causing start() loop
        to exit after current iteration completes.
        """
        self._running = False
