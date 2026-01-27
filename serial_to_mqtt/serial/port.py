# -*- coding: utf-8 -*-
"""
Serial port value objects.

This module provides value objects for serial port configuration and data.

Example usage:
    port = PortNumber(13)  # COM13
    num = port.number()  # Returns: 12 (pyserial uses 0-based indexing)

    buffer = AccumulatedBytes("")
    buffer = buffer.append(ReceivedBytes("!1;25"))
    buffer = buffer.append(ReceivedBytes(".5;38444"))
    content = buffer.content()  # "!1;25.5;38444"
"""


class PortNumber(object):
    """
    COM port number value object.

    PortNumber represents a Windows COM port number. It handles the conversion
    between Windows numbering (COM1 = 1) and pyserial numbering (COM1 = 0).

    Example usage:
        port = PortNumber(13)  # COM13
        serial_num = port.number()  # Returns: 12 for pyserial
    """

    def __init__(self, com):
        """
        Create a PortNumber for a COM port.

        Args:
            com (int): COM port number (1-based, Windows convention)
        """
        self._com = com

    def number(self):
        """
        Extract the port number for pyserial.

        Returns:
            int: Port number in pyserial format (0-based)

        Pyserial uses 0-based numbering: COM1 = 0, COM13 = 12, etc.
        """
        return self._com - 1


class ReceivedBytes(object):
    """
    Bytes received from serial connection.

    ReceivedBytes is a value object encapsulating data read from a serial port.

    Example usage:
        received = ReceivedBytes("!1;25.5;38444;")
        data = received.content()
    """

    def __init__(self, data):
        """
        Create ReceivedBytes with data.

        Args:
            data (str): The received data
        """
        self._data = data

    def content(self):
        """
        Extract the received data.

        Returns:
            str: The received bytes as string
        """
        return self._data


class EmptyBytes(object):
    """
    Empty bytes representing no data received.

    EmptyBytes is a value object representing the case where no data was
    available from the serial connection.

    Example usage:
        empty = EmptyBytes()
        data = empty.content()  # Returns: ""
    """

    def __init__(self):
        """
        Create EmptyBytes.
        """
        pass

    def content(self):
        """
        Extract the received data.

        Returns:
            str: Empty string
        """
        return ""


class AccumulatedBytes(object):
    """
    Immutable buffer for accumulating serial bytes across reads.

    AccumulatedBytes represents a running buffer of received bytes that may
    contain partial messages. New bytes are appended via the append() method
    which returns a new instance, preserving immutability.

    Example usage:
        buffer = AccumulatedBytes("")
        buffer = buffer.append(ReceivedBytes("!1;25"))
        buffer = buffer.append(ReceivedBytes(".5;38444"))
        content = buffer.content()  # "!1;25.5;38444"
    """

    def __init__(self, content):
        """
        Create AccumulatedBytes with initial content.

        Args:
            content (str): The accumulated bytes
        """
        self._content = content

    def append(self, received):
        """
        Create new AccumulatedBytes with appended data.

        Args:
            received (ReceivedBytes): New bytes to append

        Returns:
            AccumulatedBytes: New instance with appended content
        """
        return AccumulatedBytes(self._content + received.content())

    def content(self):
        """
        Extract the accumulated content.

        Returns:
            str: All accumulated bytes as string
        """
        return self._content

    def trim(self, remainder):
        """
        Create new AccumulatedBytes keeping only remainder.

        Args:
            remainder (str): The bytes to keep

        Returns:
            AccumulatedBytes: New instance with only remainder
        """
        return AccumulatedBytes(remainder)
