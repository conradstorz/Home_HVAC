from datetime import datetime
from dataclasses import dataclass
import time
import os
import sqlite3
from hypothesis import given, strategies as st

# Define the TemperatureReading dataclass to record temperature readings
@dataclass
class TemperatureReading:
    timestamp: datetime
    device_id: str
    temperature: float

# Define the TemperatureSensor dataclass to track details about individual sensors
@dataclass
class TemperatureSensor:
    sensor_id: str
    location: str
    installer: str
    installation_date: datetime
    high_record: TemperatureReading = None
    low_record: TemperatureReading = None
    latest_reading: TemperatureReading = None
    alarm_trigger_high: float = None
    alarm_trigger_low: float = None
    alarm_recipients: str = None

    def update_records(self, temperature: float):
        # Update the high and low record temperatures and dates
        if self.high_record is None or temperature > self.high_record.temperature:
            self.high_record = TemperatureReading(datetime.now(), self.sensor_id, temperature)
        if self.low_record is None or temperature < self.low_record.temperature:
            self.low_record = TemperatureReading(datetime.now(), self.sensor_id, temperature)
        # Update the latest reading
        self.latest_reading = TemperatureReading(datetime.now(), self.sensor_id, temperature)

# Define a fake temperature sensor function that generates random temperatures
@given(st.floats(min_value=-50.0, max_value=50.0, allow_nan=False, allow_infinity=False))
def fake_temperatures(temp):
    return None

# Set up the sensors
try:
    from W1ThermSensor import W1ThermSensor
    sensors = [
        TemperatureSensor(sensor.id, 'Office', 'John Doe', datetime.now())
        for sensor in W1ThermSensor.get_available_sensors()
    ]
    print("Using real sensors...")
except ImportError:
    print("W1ThermSensor module not found, using fake sensors...")
    sensors = [
        TemperatureSensor(f"sensor{i}", 'Office', 'John Doe', datetime.now())
        for i in range(3)
    ]

# Main loop to take temperature readings
while True:
    for sensor in sensors:
        if 'W1ThermSensor' in globals():
            try:
                temperature = sensor.get_temperature()
            except:
                temperature = None
        else:
            temperature = fake_temperatures()

        if temperature is not None:
            sensor.update_records(temperature)

            # Trigger an alarm if necessary
            if (sensor.alarm_trigger_high is not None and temperature > sensor.alarm_trigger_high) or \
               (sensor.alarm_trigger_low is not None and temperature < sensor.alarm_trigger_low):
                print(f"Temperature alarm triggered for sensor {sensor.sensor_id} at location {sensor.location}! Sending notification to {sensor.alarm_recipients}...")

        # Record the temperature reading in the database
        reading = TemperatureReading(
            datetime.now(),
            sensor.sensor_id,
            temperature
        )
        # ... do something with the reading (e.g., save to a database)

    # Wait 5 seconds before taking the next reading
    time.sleep(5)
