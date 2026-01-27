# -*- coding: utf-8 -*-
"""
MQTT client abstraction.

This module provides implementations for MQTT client communication.

Example usage:
    client = MqttClient(broker, port, client_id)
    result = client.connect()
    if result.successful():
        client.send(topic, payload)
        client.disconnect()
"""
from serial_to_mqtt.result.either import Right, Left


class MqttClient(object):
    """
    Paho MQTT client implementation.

    MqttClient provides methods for connecting to an MQTT broker, sending
    messages, and disconnecting. This serves as both the base class for other
    MQTT implementations and the default implementation using Paho MQTT.

    Example usage:
        broker = BrokerAddress("localhost")
        port = BrokerPort(1883)
        client_id = ClientId("sensor-1")
        client = MqttClient(broker, port, client_id)

        result = client.connect()
        if result.successful():
            client.send("test/topic", "hello")
    """

    def __init__(self, broker, port, identifier):
        """
        Create a MqttClient with broker, port, and client ID.

        Args:
            broker (BrokerAddress): The MQTT broker address
            port (BrokerPort): The MQTT broker port
            identifier (ClientId): The MQTT client identifier
        """
        self._broker = broker
        self._port = port
        self._identifier = identifier
        self._client = None

    def connect(self):
        """
        Connect to the MQTT broker.

        Returns:
            Either: Right(success) if connect succeeds, Left(error) if fails
        """
        try:
            import paho.mqtt.client as mqtt
            self._client = mqtt.Client(self._identifier.value())
            self._client.connect(self._broker.address(), self._port.number())
            self._client.loop_start()
            return Right("Connected to MQTT broker")
        except Exception as problem:
            return Left("Failed to connect to MQTT broker: {0}".format(problem))

    def send(self, topic, payload):
        """
        Send a message to an MQTT topic.

        Args:
            topic (str): The topic name
            payload (str): The message payload

        Returns:
            Either: Right(success) if send succeeds, Left(error) if fails
        """
        if self._client is None:
            return Left("MQTT client not connected")
        try:
            result = self._client.publish(topic, payload)
            if result.rc == 0:
                return Right("Message sent to topic: {0}".format(topic))
            else:
                return Left("Failed to send message, rc: {0}".format(result.rc))
        except Exception as problem:
            return Left("Failed to send MQTT message: {0}".format(problem))

    def disconnect(self):
        """
        Disconnect from the MQTT broker.

        Returns:
            Either: Right(success) if disconnect succeeds, Left(error) if fails
        """
        if self._client is None:
            return Right("MQTT client already disconnected")
        try:
            self._client.loop_stop()
            self._client.disconnect()
            self._client = None
            return Right("Disconnected from MQTT broker")
        except Exception as problem:
            return Left("Failed to disconnect from MQTT broker: {0}".format(problem))


class BrokerAddress(object):
    """
    MQTT broker address value object.

    BrokerAddress encapsulates the hostname or IP address of an MQTT broker.

    Example usage:
        broker = BrokerAddress("localhost")
        addr = broker.address()  # Returns: "localhost"
    """

    def __init__(self, value):
        """
        Create a BrokerAddress.

        Args:
            value (str): The broker hostname or IP address
        """
        self._value = value

    def address(self):
        """
        Extract the broker address.

        Returns:
            str: The broker hostname or IP address
        """
        return self._value


class BrokerPort(object):
    """
    MQTT broker port value object.

    BrokerPort encapsulates the TCP port number of an MQTT broker.

    Example usage:
        port = BrokerPort(1883)
        num = port.number()  # Returns: 1883
    """

    def __init__(self, value):
        """
        Create a BrokerPort.

        Args:
            value (int): The broker port number
        """
        self._value = value

    def number(self):
        """
        Extract the port number.

        Returns:
            int: The broker port number
        """
        return self._value


class ClientId(object):
    """
    MQTT client identifier value object.

    ClientId encapsulates the unique identifier for an MQTT client connection.

    Example usage:
        client_id = ClientId("sensor-1")
        id_str = client_id.value()  # Returns: "sensor-1"
    """

    def __init__(self, value):
        """
        Create a ClientId.

        Args:
            value (str): The client identifier
        """
        self._value = value

    def value(self):
        """
        Extract the client identifier.

        Returns:
            str: The client identifier
        """
        return self._value
