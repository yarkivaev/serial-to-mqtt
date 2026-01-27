# -*- coding: utf-8 -*-
"""
MQTT topic abstraction.

This module provides the Topic implementation for MQTT topic naming.
Business-specific topic implementations belong in the sokol-sensors project.

Example usage:
    topic = Topic("sensors/temperature")
    name = topic.name()  # Returns: "sensors/temperature"
"""


class Topic(object):
    """
    Simple topic implementation with fixed name.

    Topic encapsulates a static topic name string. This serves as both the
    base class for domain-specific topics and the default implementation
    when no domain-specific topic type is needed.

    Example usage:
        topic = Topic("test/topic")
        print(topic.name())  # Prints: test/topic
    """

    def __init__(self, value):
        """
        Create a Topic with name.

        Args:
            value (str): The topic name
        """
        self._value = value

    def name(self):
        """
        Extract the topic name.

        Returns:
            str: The MQTT topic name
        """
        return self._value
