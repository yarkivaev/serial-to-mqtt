# -*- coding: utf-8 -*-
"""
Publisher abstraction for publishing sensor readings.

This module provides the Publisher implementation for publishing readings to
MQTT brokers.

Example usage:
    publisher = Publisher(client, topic, formatter)
    reading = TemperatureReading(epoch, celsius)

    result = publisher.publish(reading)
    if result.successful():
        print("Published successfully")
"""


class Publisher(object):
    """
    MQTT implementation of publisher.

    Publisher coordinates an MQTT client, topic, and formatter to
    publish sensor readings to MQTT topics. This serves as both the
    base class for domain-specific publishers and the default implementation
    when no domain-specific publisher is needed.

    Example usage:
        client = MqttClient(broker, port, client_id)
        topic = Topic("sensors/temperature")
        formatter = Formatter()
        publisher = Publisher(client, topic, formatter)

        reading = TemperatureReading(epoch, celsius)
        result = publisher.publish(reading)
    """

    def __init__(self, client, topic, formatter):
        """
        Create a Publisher with client, topic, and formatter.

        Args:
            client (MqttClient): The MQTT client
            topic (Topic): The topic to publish to
            formatter (Formatter): The payload formatter
        """
        self._client = client
        self._topic = topic
        self._formatter = formatter

    def publish(self, reading):
        """
        Publish a reading to the MQTT topic.

        Args:
            reading (Reading): The reading to publish

        Returns:
            Either: Right(success) if publish succeeds, Left(error) if fails

        This method formats the reading and sends it via the MQTT client.
        """
        payload = self._formatter.format(reading)
        return self._client.send(self._topic.name(), payload)
