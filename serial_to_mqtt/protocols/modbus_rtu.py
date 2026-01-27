# -*- coding: utf-8 -*-
"""
Modbus RTU protocol implementation.

This module implements standard Modbus RTU protocol with CRC-16 checksum.
This is a generic protocol that can work with any sensor type through
dependency injection of measurement and reading factories.

Modbus RTU uses CRC-16 with polynomial 0x8005 (reversed form of standard).

Example usage:
    from serial_to_mqtt.domain.factory import MeasurementFactory
    from serial_to_mqtt.domain.factory import ReadingFactory
    from serial_to_mqtt.domain.reading import Clock
    measurement_factory = MeasurementFactory("celsius", "°C")
    reading_factory = ReadingFactory()
    clock = Clock()
    protocol = ModbusRtuProtocol(measurement_factory, reading_factory, clock)
    raw_bytes = b"\x01\x03\x04\x00\x0a\x00\x01\xdd\xf4"
    result = protocol.parse(raw_bytes)
    if result.successful():
        reading = result.value()
"""
from serial_to_mqtt.result.either import Right, Left
from serial_to_mqtt.domain.protocol import Protocol
from serial_to_mqtt.protocols.checksum import Checksum


class ModbusRtuProtocol(Protocol):
    """
    Modbus RTU protocol implementation with configurable factories.

    ModbusRtuProtocol parses sensor messages in standard Modbus RTU format
    and validates them using CRC-16. It uses injected factories to create
    domain-specific measurements and readings, enabling protocol reuse
    across different measurement types.

    This implementation assumes function code 03 (Read Holding Registers)
    with measurement value in first register.

    Example usage:
        from serial_to_mqtt.domain.factory import MeasurementFactory
        from serial_to_mqtt.domain.factory import ReadingFactory
        from serial_to_mqtt.domain.reading import Clock
        measurement_factory = MeasurementFactory("celsius", "°C")
        reading_factory = ReadingFactory()
        clock = Clock()
        protocol = ModbusRtuProtocol(measurement_factory, reading_factory, clock)
        result = protocol.parse(raw_bytes)
        if result.successful():
            reading = result.value()
    """

    def __init__(self, measurement_factory, reading_factory, clock):
        """
        Create a ModbusRtuProtocol with factories and clock.

        Args:
            measurement_factory (MeasurementFactory): Factory for measurements
            reading_factory (ReadingFactory): Factory for readings
            clock (Clock): Clock for getting current time
        """
        self._checksum = ModbusCrc16(ModbusCrc16Calculator())
        self._measurement_factory = measurement_factory
        self._reading_factory = reading_factory
        self._clock = clock

    def parse(self, bytes):
        """
        Parse raw bytes into a Reading.

        Args:
            bytes: Raw bytes received from serial connection

        Returns:
            Either: Right(Reading) if parsing succeeds, Left(error) if fails

        Parsing steps:
        1. Validate minimum length
        2. Validate CRC-16
        3. Parse function code
        4. Extract numeric value
        5. Use factories to create measurement and reading with timestamp
        """
        if len(bytes) < 5:
            return Left("Modbus RTU message too short")
        if not self._checksum.valid(bytes):
            return Left("Invalid Modbus RTU CRC-16")
        try:
            function_code = ord(bytes[1]) if isinstance(bytes[1], str) else bytes[1]
            if function_code != 3:
                return Left("Unsupported Modbus function code: {0}".format(function_code))
            byte_count = ord(bytes[2]) if isinstance(bytes[2], str) else bytes[2]
            if len(bytes) < 3 + byte_count + 2:
                return Left("Modbus RTU message length mismatch")
            high_byte = ord(bytes[3]) if isinstance(bytes[3], str) else bytes[3]
            low_byte = ord(bytes[4]) if isinstance(bytes[4], str) else bytes[4]
            raw_value = (high_byte << 8) | low_byte
            numeric = float(raw_value) / 10.0
            measurement = self._measurement_factory.create(numeric)
            epoch = self._clock.epoch()
            reading = self._reading_factory.create(epoch, measurement)
            return Right(reading)
        except Exception as problem:
            return Left("Failed to parse Modbus RTU message: {0}".format(problem))


class ModbusCrc16(Checksum):
    """
    Modbus CRC-16 checksum validator.

    ModbusCrc16 validates Modbus RTU messages using standard CRC-16 algorithm.
    The CRC is the last 2 bytes of the message in little-endian format.

    Example usage:
        calculator = ModbusCrc16Calculator()
        checksum = ModbusCrc16(calculator)
        is_valid = checksum.valid(message_bytes)
    """

    def __init__(self, calculator):
        """
        Create a ModbusCrc16 with calculator.

        Args:
            calculator (ModbusCrc16Calculator): The CRC calculator
        """
        self._calculator = calculator

    def valid(self, bytes):
        """
        Validate a Modbus RTU message using CRC-16.

        Args:
            bytes: The message bytes to validate

        Returns:
            bool: True if CRC matches, False otherwise
        """
        if len(bytes) < 3:
            return False
        data = bytes[:-2]
        crc_low = ord(bytes[-2]) if isinstance(bytes[-2], str) else bytes[-2]
        crc_high = ord(bytes[-1]) if isinstance(bytes[-1], str) else bytes[-1]
        expected = (crc_high << 8) | crc_low
        calculated = self._calculator.calculate(data)
        return calculated == expected


class ModbusCrc16Calculator(object):
    """
    Modbus CRC-16 calculator.

    ModbusCrc16Calculator implements the standard Modbus CRC-16 algorithm.
    This uses polynomial 0x8005 in normal form or 0xA001 in reversed form.

    Algorithm:
    1. Initialize with 0xFFFF
    2. For each byte:
       - XOR with CRC
       - For 8 bits:
         - If LSB is 1: shift right and XOR with 0xA001
         - Else: shift right

    Example usage:
        calculator = ModbusCrc16Calculator()
        crc = calculator.calculate(data_bytes)
    """

    def __init__(self):
        """
        Create a ModbusCrc16Calculator.
        """
        pass

    def calculate(self, data):
        """
        Calculate Modbus CRC-16 for data.

        Args:
            data: The data bytes to checksum

        Returns:
            int: The calculated CRC-16 value
        """
        crc = 0xFFFF
        for byte in data:
            value = ord(byte) if isinstance(byte, str) else byte
            crc = crc ^ value
            for bit in range(8):
                if crc & 0x0001:
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc = crc >> 1
        return crc
