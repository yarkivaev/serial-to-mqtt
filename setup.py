"""
Setup configuration for serial-to-mqtt library.

This package provides protocol-agnostic serial sensor communication with MQTT
publishing support. Supports Modbus RTU protocol.
"""
from distutils.core import setup

setup(
    name='serial-to-mqtt',
    version='1.0.0',
    description='Protocol-agnostic serial sensor to MQTT library',
    author='SOKOL',
    packages=[
        'serial_to_mqtt',
        'serial_to_mqtt.domain',
        'serial_to_mqtt.protocols',
        'serial_to_mqtt.serial',
        'serial_to_mqtt.mqtt',
        'serial_to_mqtt.result'
    ],
    install_requires=[
        'pyserial==3.4'
    ],
    python_requires='>=3.3'
)
