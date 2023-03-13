from datetime import datetime
from dataclasses import dataclass
import time
import os
from typing import Optional

try:
    from w1thermsensor import W1ThermSensor
except ImportError:
    W1ThermSensor = None
    from hypothesis import strategies as st

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
    high_record: Optional[TemperatureReading] = None
    low_record: Optional[TemperatureReading] = None
    latest_reading: Optional[TemperatureReading] = None
    alarm_trigger_high: Optional[float] = None
    alarm_trigger_low: Optional[float] = None
    alarm_recipients: Optional[str] = None

    def update_records(self, temperature: float):
        # Update the high and low record temperatures and dates
        if self.high_record is None or temperature > self.high_record.temperature:
            self.high_record = TemperatureReading(datetime.now(), self.sensor_id, temperature)
        if self.low_record is None or temperature < self.low_record.temperature:
            self.low_record = TemperatureReading(datetime.now(), self.sensor_id, temperature)
        # Update the latest reading
        self.latest_reading = TemperatureReading(datetime.now(), self.sensor_id, temperature)

if W1ThermSensor is not None:
    # Set up the sensors
    sensors = [
        TemperatureSensor(sensor.id, 'Office', 'John Doe', datetime.now())
        for sensor in W1ThermSensor.get_available_sensors()
    ]
else:
    # Use Hypothesis to generate mock data
    @st.composite
    def fake_temperatures(draw):
        return draw(st.floats(min_value=-20, max_value=50))

    sensors = [
        TemperatureSensor(f"sensor_{i}", 'Office', 'John Doe', datetime.now())
        for i in range(3)
    ]

# Main loop to take temperature readings
while True:
    for sensor in sensors:
        if W1ThermSensor is not None:
            try:
                temperature = sensor.get_temperature()
            except:
                temperature = None
        else:
            temperature = fake_temperatures().example()

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
