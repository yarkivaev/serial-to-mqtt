# -*- coding: utf-8 -*-
"""
Collection of pipelines with unified interface.

This module provides Pipelines class which manages multiple
pipelines as a single unit with unified start/stop.

Example usage:
    pipelines = Pipelines([
        AsyncPipeline(LoopedPipeline(SensorPipeline(...))),
        AsyncPipeline(LoopedPipeline(SensorPipeline(...))),
    ])
    pipelines.start()  # Starts all
    pipelines.stop()   # Stops all (waits for completion)
"""
from serial_to_mqtt.domain.pipeline import Pipeline


class Pipelines(Pipeline):
    """
    Collection of pipelines with unified interface.

    Pipelines manages multiple pipelines as one, allowing
    unified start and stop operations across all items.

    Example usage:
        items = [async1, async2, async3]
        pipelines = Pipelines(items)
        pipelines.start()  # Starts all pipelines
        pipelines.stop()   # Stops all and waits for completion
    """

    def __init__(self, items):
        """
        Create a Pipelines collection with items.

        Args:
            items: List of Pipeline instances to manage
        """
        self._items = items

    def start(self):
        """
        Start all pipelines in the collection.

        Iterates through all items and calls start() on each.
        """
        for item in self._items:
            item.start()

    def stop(self):
        """
        Stop all pipelines in the collection.

        Iterates through all items and calls stop() on each.
        Blocks until all pipelines have stopped.
        """
        for item in self._items:
            item.stop()
