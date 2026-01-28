# -*- coding: utf-8 -*-
"""
Pipeline abstraction for sensor reading and publishing.

This module provides the Pipeline interface and SensorPipeline
implementation for coordinating sensor reads with publishers.

Example usage:
    sensor = Sensor(connection, protocol)
    publisher = Publisher(client, topic, formatter)
    config = SensorConfig(3, "ksum", "machine1", "oil")
    console = Console(sys.stdout)

    pipeline = SensorPipeline(sensor, publisher, config, console)
    pipeline.start()  # Executes one iteration
"""


class Pipeline(object):
    """
    Interface for pipelines.

    Pipeline defines the contract for sensor data processing.
    All implementations must provide start() and stop() methods
    for uniform lifecycle management.

    Example usage:
        pipeline = SomePipeline(...)
        pipeline.start()
        pipeline.stop()
    """

    def start(self):
        """
        Start the pipeline.

        Raises:
            NotImplementedError: Subclasses must implement this method
        """
        raise NotImplementedError("Subclasses must implement start")

    def stop(self):
        """
        Stop the pipeline.

        Raises:
            NotImplementedError: Subclasses must implement this method
        """
        raise NotImplementedError("Subclasses must implement stop")


class SensorPipeline(Pipeline):
    """
    Pipeline that reads sensor and publishes reading.

    SensorPipeline coordinates one sensor read with one publish.
    Each start() call executes exactly one iteration: read sensor,
    check if publishable, publish if successful.

    Example usage:
        sensor = Sensor(connection, protocol)
        publisher = Publisher(client, topic, formatter)
        config = SensorConfig(3, "ksum", "machine1", "oil")
        console = Console(sys.stdout)

        pipeline = SensorPipeline(sensor, publisher, config, console)
        pipeline.start()  # One iteration
        pipeline.start()  # Another iteration
    """

    def __init__(self, sensor, publisher, config, console):
        """
        Create a SensorPipeline with collaborators.

        Args:
            sensor: Sensor for reading measurements
            publisher: Publisher for sending readings
            config: Configuration with port number
            console: Console for error messages
        """
        self._sensor = sensor
        self._publisher = publisher
        self._config = config
        self._console = console

    def start(self):
        """
        Execute one iteration: read, check, publish.

        Reads from sensor, checks if reading is publishable,
        and publishes if successful. Logs errors to console.
        """
        result = self._sensor.read()
        if result.successful():
            reading = result.value()
            if reading.publishable():
                self._publisher.publish(reading)
        else:
            self._console.say("COM{0}: {1}".format(
                self._config.port(), result.error()))

    def stop(self):
        """
        No-op for single-execution pipeline.

        SensorPipeline executes one iteration per start() call,
        so stop() has no effect.
        """
        pass
