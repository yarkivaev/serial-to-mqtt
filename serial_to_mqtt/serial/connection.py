# -*- coding: utf-8 -*-
"""
Serial connection abstraction.

This module provides implementations for serial port
communication with automatic reconnection support.

Example usage:
    config = SerialConfig(9600, 8, "N", 1)
    port = PortNumber(13)
    raw = SerialConnection(port, config)

    result = raw.open()
    if result.successful():
        bytes_result = raw.receive()
        if bytes_result.successful():
            data = bytes_result.value().content()

    # Framed connection for complete message handling:
    delay = Delay(0.1)
    delayed = DelayedConnection(raw, delay)
    delimiter = KsumDelimiter()
    framed = FramedConnection(delayed, delimiter)
    result = framed.receive()  # Returns complete messages only
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


class DelayedConnection(object):
    """
    Connection decorator that adds delay after each read.

    DelayedConnection wraps another connection and waits after
    each receive() call, giving time for data to accumulate.

    Example usage:
        raw = SerialConnection(port, config)
        delay = Delay(0.1)
        delayed = DelayedConnection(raw, delay)
    """

    def __init__(self, connection, delay):
        """
        Create a DelayedConnection.

        Args:
            connection: Connection to wrap
            delay: Delay to wait after each read
        """
        self._connection = connection
        self._delay = delay

    def open(self):
        """
        Open the underlying connection.

        Returns:
            Either: Right(success) if open succeeds, Left(error) if fails
        """
        return self._connection.open()

    def receive(self):
        """
        Receive bytes and wait.

        Returns:
            Either: Right(ReceivedBytes) if successful, Left(error) if failed

        This method reads from inner connection, then waits.
        """
        result = self._connection.receive()
        self._delay.wait()
        return result

    def close(self):
        """
        Close the underlying connection.

        Returns:
            Either: Right(success) if close succeeds, Left(error) if fails
        """
        return self._connection.close()


class FramedConnection(object):
    """
    Framed connection that accumulates bytes until complete messages.

    FramedConnection loops calling the inner connection until
    delimiter finds a complete message. No delay logic - use
    DelayedConnection as inner connection for delays.

    Example usage:
        delayed = DelayedConnection(raw, Delay(0.1))
        delimiter = KsumDelimiter()
        framed = FramedConnection(delayed, delimiter)
    """

    def __init__(self, connection, delimiter):
        """
        Create a FramedConnection.

        Args:
            connection: Connection to wrap (typically DelayedConnection)
            delimiter: Delimiter for identifying message boundaries
        """
        self._connection = connection
        self._delimiter = delimiter
        self._accumulated = AccumulatedBytes("")

    def open(self):
        """
        Open the underlying connection.

        Returns:
            Either: Right(success) if open succeeds, Left(error) if fails
        """
        return self._connection.open()

    def receive(self):
        """
        Receive complete message from connection.

        Returns:
            Either: Right(ReceivedBytes) with complete message, Left(error) if failed

        This method loops until a complete message is found.
        """
        while True:
            result = self._connection.receive()
            if not result.successful():
                return result
            self._accumulated = self._accumulated.append(result.value())
            extraction = self._delimiter.extract(self._accumulated.content())
            if not extraction.empty():
                first = extraction.messages()[0]
                content = self._accumulated.content()
                position = content.find(first) + len(first)
                self._accumulated = self._accumulated.trim(content[position:])
                return Right(ReceivedBytes(first))

    def close(self):
        """
        Close the underlying connection.

        Returns:
            Either: Right(success) if close succeeds, Left(error) if fails
        """
        return self._connection.close()
