# serial-to-mqtt

Generic protocol-agnostic serial sensor to MQTT library.

## Purpose

This library provides abstractions for reading sensors via serial connections and publishing measurements to MQTT brokers. It is completely generic and does not know about specific measurement types (temperature, pressure, etc.).

Supported protocols:
- **Modbus RTU**: Standard Modbus protocol with CRC-16

## Architecture

serial-to-mqtt is a generic library. You define your own domain-specific types in your application and inject them via factories.

### Generic Types Provided

**Measurement Abstraction:**
- `Measurement` - Generic measurement with `value()` and `unit()`

**Unit Abstraction:**
- `Unit` - Generic unit with `name()` and `symbol()`

**Reading Abstraction:**
- `Reading` - Generic timestamped measurement

**Factory Pattern:**
- `MeasurementFactory` - Creates measurements from numeric values
- `ReadingFactory` - Creates readings from measurements

## Installation

```bash
pip install -r requirements.txt
python setup.py install
```

Requires Python 3.3+ and pyserial 3.4.

## Usage

### Using with Default Generic Types

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

# Create factories and clock for your sensor
measurement_factory = MeasurementFactory("celsius", "°C")
reading_factory = ReadingFactory()
clock = Clock()

# Configure serial sensor with factory-injected protocol
port = PortNumber(13)
config = SerialConfig()
connection = SerialConnection(port, config)
connection.open()

protocol = ModbusRtuProtocol(measurement_factory, reading_factory, clock)
delay = Delay()
sensor = Sensor(connection, protocol, delay)

# Configure MQTT publisher
broker = BrokerAddress("localhost")
mqtt_port = BrokerPort(1883)
client_id = ClientId("sensor-1")
mqtt_client = MqttClient(broker, mqtt_port, client_id)
mqtt_client.connect()

topic = Topic("sensors/temperature")
formatter = Formatter()
publisher = Publisher(mqtt_client, topic, formatter)

# Read and publish
result = sensor.read()
if result.successful():
    reading = result.value()
    measurement = reading.measurement()
    print(measurement.value())  # Numeric value
    print(measurement.unit().name())  # "celsius"
    publisher.publish(reading)
```

### Using with Custom Domain Types

```python
# 1. Define your domain types
from serial_to_mqtt.domain.measurement import Measurement
from serial_to_mqtt.domain.unit import Unit

class Celsius(Unit):
    def __init__(self):
        pass

    def name(self):
        return "celsius"

    def symbol(self):
        return "°C"

class Temperature(Measurement):
    def __init__(self, unit, numeric):
        self._unit = unit
        self._numeric = numeric

    def value(self):
        return self._numeric

    def unit(self):
        return self._unit

# 2. Define factories
from serial_to_mqtt.domain.factory import MeasurementFactory, ReadingFactory

class TemperatureMeasurementFactory(MeasurementFactory):
    def __init__(self):
        self._unit = Celsius()

    def create(self, numeric):
        return Temperature(self._unit, numeric)

# 3. Use with protocols
from serial_to_mqtt.domain.reading import Clock
factory = TemperatureMeasurementFactory()
reading_factory = ReadingFactory()
clock = Clock()
protocol = ModbusRtuProtocol(factory, reading_factory, clock)
```

## Generic Measurement System

### Core Concepts

The library uses **dependency injection** and the **factory pattern** to decouple protocols from specific measurement types.

**Measurement** - Can represent any physical quantity:
```python
from serial_to_mqtt.domain.measurement import Measurement
from serial_to_mqtt.domain.unit import Unit

# Temperature
celsius = Unit("celsius", "°C")
temp = Measurement(celsius, 25.5)

# Voltage
volt = Unit("volt", "V")
voltage = Measurement(volt, 12.5)

# Pressure
pascal = Unit("pascal", "Pa")
pressure = Measurement(pascal, 101325.0)

# Any other sensor type
ampere = Unit("ampere", "A")
current = Measurement(ampere, 2.5)
```

**Unit** - Can represent any unit:
```python
from serial_to_mqtt.domain.unit import Unit

# Any unit you need
celsius = Unit("celsius", "°C")
fahrenheit = Unit("fahrenheit", "°F")
pascal = Unit("pascal", "Pa")
volt = Unit("volt", "V")
ampere = Unit("ampere", "A")
```

**Factory Pattern** - Protocols use factories to create measurements:
```python
from serial_to_mqtt.domain.factory import MeasurementFactory, ReadingFactory
from serial_to_mqtt.domain.reading import Clock

# Create factory for voltage measurements
voltage_factory = MeasurementFactory("volt", "V")
reading_factory = ReadingFactory()
clock = Clock()

# Inject into protocol
protocol = ModbusRtuProtocol(voltage_factory, reading_factory, clock)

# Protocol creates Voltage measurements without knowing the type
result = protocol.parse(raw_bytes)
if result.successful():
    reading = result.value()
    measurement = reading.measurement()
    print(measurement.value())  # e.g., 12.5
    print(measurement.unit().name())  # "volt"
```

### Benefits

**Generic Library:**
- Works with ANY sensor type (temperature, voltage, pressure, flow, etc.)
- No coupling to specific measurement domains
- Reusable across different projects

**Clean Separation:**
- Library: Generic serial/MQTT communication
- Application: Domain-specific types (Temperature, etc.)
- Follows single responsibility principle

**Extensibility:**
- Easy to add new measurement types in your application
- No need to modify library for new domains
- Each application defines its own types

**Elegant Objects Compliance:**
- Dependency injection via factories
- Pure polymorphism - no type introspection
- Immutable value objects
- CQRS methods (queries are nouns)
- 1-4 attributes per class
- No utility classes
- No static methods

## Extending

### Add New Protocols

Implement the `Protocol` interface:

```python
from serial_to_mqtt.domain.protocol import Protocol
from serial_to_mqtt.result.either import Right, Left

class CustomProtocol(Protocol):
    def __init__(self, measurement_factory, reading_factory, clock):
        self._measurement_factory = measurement_factory
        self._reading_factory = reading_factory
        self._clock = clock

    def parse(self, bytes):
        # Parse bytes to extract numeric value
        try:
            numeric = float(parse_value_from_bytes(bytes))

            # Use factories and clock to create measurement and reading
            measurement = self._measurement_factory.create(numeric)
            epoch = self._clock.epoch()
            reading = self._reading_factory.create(epoch, measurement)

            return Right(reading)
        except Exception as error:
            return Left("Parse failed: {0}".format(error))
```

The library remains generic and reusable across different domains.

## Testing

```bash
cd serial-to-mqtt
python3 -m unittest discover tests -v
```

All tests use generic `Measurement` and `Unit` types.

## Design Principles

- **Zero type introspection**: No `isinstance()` checks, pure polymorphism
- **Factory pattern**: Protocols don't know concrete measurement types
- **Dependency injection**: Factories injected via constructors
- **Immutable value objects**: All measurements, units, and readings are immutable
- **CQRS methods**: `value()`, `unit()`, `measurement()` are nouns (queries)
- **Single responsibility**: Library handles communication, applications handle domain types
