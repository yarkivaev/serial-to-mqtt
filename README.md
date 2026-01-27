# serial-to-mqtt

Generic protocol-agnostic serial sensor to MQTT library.

## Installation

```bash
pip install -e .
```

Requires Python 3.3+ and pyserial 2.7.

## Usage

```python
from serial_to_mqtt.domain.sensor import Sensor, Delay
from serial_to_mqtt.serial.connection import SerialConnection, SerialConfig
from serial_to_mqtt.serial.port import PortNumber
from serial_to_mqtt.domain.factory import MeasurementFactory, ReadingFactory
from serial_to_mqtt.domain.reading import Clock
from serial_to_mqtt.protocols.modbus_rtu import ModbusRtuProtocol
from serial_to_mqtt.mqtt.client import MqttClient, BrokerAddress, BrokerPort, ClientId
from serial_to_mqtt.mqtt.topic import Topic
from serial_to_mqtt.mqtt.payload import Formatter
from serial_to_mqtt.domain.publisher import Publisher

# Setup sensor
port = PortNumber(13)
connection = SerialConnection(port, SerialConfig())
connection.open()

measurement_factory = MeasurementFactory("celsius", "°C")
reading_factory = ReadingFactory()
clock = Clock()
protocol = ModbusRtuProtocol(measurement_factory, reading_factory, clock)
sensor = Sensor(connection, protocol, Delay())

# Setup MQTT
mqtt = MqttClient(BrokerAddress("localhost"), BrokerPort(1883), ClientId("sensor-1"))
mqtt.connect()
publisher = Publisher(mqtt, Topic("sensors/temperature"), Formatter())

# Read and publish
result = sensor.read()
if result.successful():
    publisher.publish(result.value())
```

## Testing

```bash
python -m unittest discover tests -v
```

## Supported Protocols

- **Modbus RTU** - Standard Modbus protocol with CRC-16

## Design

- Factory pattern for dependency injection
- Either monad for error handling
- Immutable value objects
- No static methods
