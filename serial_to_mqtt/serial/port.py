# -*- coding: utf-8 -*-
"""
Serial port value objects.

This module provides value objects for serial port configuration and data.

Example usage:
    port = PortNumber(13)  # COM13
    num = port.number()  # Returns: 12 (pyserial uses 0-based indexing)
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
