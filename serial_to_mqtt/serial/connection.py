# -*- coding: utf-8 -*-
"""
Serial connection abstraction.

This module provides implementations for serial port
communication with automatic reconnection support.

Example usage:
    config = SerialConfig(9600, 8, "N", 1)
    port = PortNumber(13)
    connection = SerialConnection(port, config)

    result = connection.open()
    if result.successful():
        bytes_result = connection.receive()
        if bytes_result.successful():
            data = bytes_result.value().content()

    # Buffered connection for partial message handling:
    delimiter = KsumDelimiter()
    buffered = BufferedConnection(connection, delimiter)
    result = buffered.receive()  # Returns complete messages only
"""
import time
from serial_to_mqtt.result.either import Right, Left
from serial_to_mqtt.serial.port import ReceivedBytes, AccumulatedBytes


class SerialConnection(object):
    """
    PySerial implementation of serial connection.

    SerialConnection provides methods for opening, reading, and closing
    serial ports. It uses Either monad for error handling without null.
    This serves as both the base class for other serial implementations
    and the default implementation using PySerial.

    Example usage:
        config = SerialConfig(9600, 8, "N", 1)
        port = PortNumber(13)
        connection = SerialConnection(port, config)

        result = connection.open()
        if result.successful():
            data_result = connection.receive()
    """

    def __init__(self, port, config):
        """
        Create a SerialConnection with port and configuration.

        Args:
            port (PortNumber): The COM port number
            config (SerialConfig): Serial port configuration
        """
        self._port = port
        self._config = config
        self._serial = None

    def open(self):
        """
        Open the serial connection.

        Returns:
            Either: Right(success) if open succeeds, Left(error) if fails
        """
        try:
            import serial
            self._serial = serial.Serial(
                port=self._port.number(),
                baudrate=self._config.baudrate(),
                bytesize=self._config.bytesize(),
                parity=self._config.parity(),
                stopbits=self._config.stopbits()
            )
            return Right("Serial connection opened")
        except Exception as problem:
            return Left("Failed to open serial port: {0}".format(problem))

    def receive(self):
        """
        Receive bytes from the serial connection.

        Returns:
            Either: Right(ReceivedBytes) if successful, Left(error) if failed

        This method reads all available bytes from the input buffer.
        """
        if self._serial is None:
            return Left("Serial connection not opened")
        try:
            waiting = self._serial.inWaiting()
            if waiting > 0:
                data = self._serial.read(waiting)
                text = data.decode('ascii', errors='replace')
                return Right(ReceivedBytes(text))
            else:
                return Right(ReceivedBytes(""))
        except Exception as problem:
            return Left("Failed to receive from serial port: {0}".format(problem))

    def close(self):
        """
        Close the serial connection.

        Returns:
            Either: Right(success) if close succeeds, Left(error) if fails
        """
        if self._serial is None:
            return Right("Serial connection already closed")
        try:
            self._serial.close()
            self._serial = None
            return Right("Serial connection closed")
        except Exception as problem:
            return Left("Failed to close serial port: {0}".format(problem))


class SerialConfig(object):
    """
    Serial port configuration value object.

    SerialConfig encapsulates serial port settings: baudrate, bytesize,
    parity, and stopbits.

    Example usage:
        config = SerialConfig(9600, 8, "N", 1)
        rate = config.baudrate()  # Returns: 9600
    """

    def __init__(self, baud=9600, bytesize=8, parity="N", stopbits=1):
        """
        Create a SerialConfig with settings.

        Args:
            baud (int): Baud rate (default: 9600)
            bytesize (int): Number of data bits (default: 8)
            parity (str): Parity ('N', 'E', 'O') (default: 'N')
            stopbits (int): Number of stop bits (default: 1)
        """
        self._baud = baud
        self._bytesize = bytesize
        self._parity = parity
        self._stopbits = stopbits

    def baudrate(self):
        """
        Extract the baud rate.

        Returns:
            int: The baud rate
        """
        return self._baud

    def bytesize(self):
        """
        Extract the byte size.

        Returns:
            int: The number of data bits
        """
        return self._bytesize

    def parity(self):
        """
        Extract the parity setting.

        Returns:
            str: The parity setting
        """
        return self._parity

    def stopbits(self):
        """
        Extract the stop bits setting.

        Returns:
            int: The number of stop bits
        """
        return self._stopbits


class BufferedConnection(object):
    """
    Buffered serial connection that accumulates bytes until complete messages.

    BufferedConnection wraps a SerialConnection and uses a delimiter to
    identify when complete messages are available. It maintains state between
    calls to handle messages split across multiple reads.

    Example usage:
        connection = SerialConnection(port, config)
        delimiter = KsumDelimiter()
        buffered = BufferedConnection(connection, delimiter)

        result = buffered.receive()  # Returns only complete messages
    """

    def __init__(self, connection, delimiter):
        """
        Create a BufferedConnection wrapping a connection.

        Args:
            connection: SerialConnection to wrap
            delimiter: Delimiter for identifying message boundaries
        """
        self._connection = connection
        self._delimiter = delimiter
        self._accumulated = AccumulatedBytes("")

    def open(self):
        """
        Open the underlying serial connection.

        Returns:
            Either: Right(success) if open succeeds, Left(error) if fails
        """
        return self._connection.open()

    def receive(self):
        """
        Receive complete message from serial connection.

        Returns:
            Either: Right(ReceivedBytes) with complete message, Left(error) if failed

        This method accumulates bytes until a complete message is found.
        If multiple messages are available, returns the first one.
        """
        result = self._connection.receive()
        if not result.successful():
            return result
        self._accumulated = self._accumulated.append(result.value())
        extraction = self._delimiter.extract(self._accumulated.content())
        if extraction.empty():
            return Right(ReceivedBytes(""))
        self._accumulated = self._accumulated.trim(extraction.remainder())
        return Right(ReceivedBytes(extraction.messages()[0]))

    def close(self):
        """
        Close the underlying serial connection.

        Returns:
            Either: Right(success) if close succeeds, Left(error) if fails
        """
        return self._connection.close()
