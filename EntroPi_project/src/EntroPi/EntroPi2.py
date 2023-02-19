"""A ChatGPT inspired implementation triggered by the idea to use dataclasses.
        CahtGPT suggested using the SQLlite database."""

from datetime import datetime
from dataclasses import dataclass
import time
import os

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

# Set up the sensors
sensors = [
    TemperatureSensor(sensor.id, 'Office', 'John Doe', datetime.now())
    for sensor in W1ThermSensor.get_available_sensors()
]

# Main loop to take temperature readings
while True:
    for sensor in sensors:
        try:
            temperature = sensor.get_temperature()
        except:
            temperature = None

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
