# -*- coding: utf-8 -*-
"""
Message delimiter abstractions for serial communication.

This module provides classes for extracting complete messages from
byte streams where messages may arrive in chunks.

Example usage:
    extraction = Extraction(["!1;25.5;38444"], "!2;30")
    messages = extraction.messages()  # ["!1;25.5;38444"]
    remainder = extraction.remainder()  # "!2;30"
"""


class Extraction(object):
    """
    Result of extracting messages from byte stream.

    Extraction encapsulates complete messages ready for parsing and
    remaining bytes that form incomplete messages.

    Example usage:
        extraction = Extraction(["!1;25.5;38444"], "!2;30")
        messages = extraction.messages()  # ["!1;25.5;38444"]
        remainder = extraction.remainder()  # "!2;30"
        empty = extraction.empty()  # False
    """

    def __init__(self, messages, remainder):
        """
        Create an Extraction with messages and remainder.

        Args:
            messages (list): List of complete message strings
            remainder (str): Remaining incomplete bytes
        """
        self._messages = messages
        self._remainder = remainder

    def messages(self):
        """
        Extract the list of complete messages.

        Returns:
            list: Complete message strings ready for parsing
        """
        return self._messages

    def remainder(self):
        """
        Extract the remaining incomplete bytes.

        Returns:
            str: Bytes that do not form complete messages yet
        """
        return self._remainder

    def empty(self):
        """
        Query whether no complete messages were found.

        Returns:
            bool: True if no complete messages available
        """
        return len(self._messages) == 0
