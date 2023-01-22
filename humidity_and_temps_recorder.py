#!/usr/bin/env python
# -*- coding: utf-8 -*-

from w1Therm import read_temperatures
from dht11_test import get_humidity
from loguru import logger
from datetime import datetime
import time
import csv
import os.path
from os import path

""" TODO get outside temperature and humidity from open weather map and place into csv database with each reading of sensors.
TODO note that once per 12 minutes is probably frequent enough to check temps and humidity
Thank you for subscribing to Free OpenWeatherMap!

API key:
- Your API key is 5a51770d8fa87227c5c1a07f3f9240fd
- Within the next couple of hours, it will be activated and ready to use
- You can later create more API keys on your account page
- Please, always use your API key in each API call

Endpoint:
- Please, use the endpoint api.openweathermap.org for your API calls
- Example of API call:
api.openweathermap.org/data/2.5/weather?q=London,uk&APPID=5a51770d8fa87227c5c1a07f3f9240fd

lat = '38.317139'
lon = '-85.868167'
API = '5a51770d8fa87227c5c1a07f3f9240fd'
url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API}"

Useful links:
- API documentation https://openweathermap.org/api
- Details of your plan https://openweathermap.org/price
- Please, note that 16-days daily forecast and History API are not available for Free subscribers
"""


"""
from subprocess import check_output
lcd.message('Local IP Address:\n')
lcd.message(ips2 = check_output(['hostname', '--all-ip-addresses']).decode('utf-8'))

"""
@logger.catch
def write_csv(device_data, directory="."):
    # Open the output CSV file and write 'the results
    print(f'\ndevice_data:\n{device_data}\n')
    first_key = list(device_data)[0]
    # print(f'first key: {first_key}')
    first_device_values = device_data[first_key]
    fieldnames = first_device_values.keys() # retrieve keys from nested dictionaries
    print(f'\nfilednames:\n{fieldnames}\n')    
    out_csv = f'{datetime.now().strftime("%Y%m%d")}_HVAC_temps.csv'
    # check if file exists and write headers if new file
    if not path.exists(out_csv):
        with open(out_csv, 'w', newline='') as h:
            writer = csv.DictWriter(h, fieldnames=fieldnames)
            writer.writeheader()    
    else:
        with open(out_csv, 'a', newline='') as h:
            writer = csv.DictWriter(h, fieldnames=fieldnames)            
            # Write a row for each location
            for device, values in device_data.items():
                writer.writerow(values)
    print(f'Output file saved as {out_csv}.')    


@logger.catch
def main_data_gathering_loop():
    time_delay = 0
    sensors_reporting = read_temperatures()
    print(sensors_reporting)
    while True:
        # TODO Compress_CSV_files() # CSV files need to be compressed periodically
        sensors_reporting = read_temperatures()
        write_csv(sensors_reporting['all records'])
        if time_delay >= 14:
            # send_to_thingspeak(latest readings)
            pass
        print("Sleeping 1 second...")
        time_delay =+ 1
        time.sleep(1)


# TODO make a seperate script webserver that displays all details and offers ability to rename sensors
# TODO find a way to make IP address discoverable without attaching a monitor to the pi
# TODO maybe use a common name that can be typed into a web browser on the same intranet
sensors_reporting = read_temperatures()
print(f'sensors reporting:\n{sensors_reporting}')
for sensor, value in sensors_reporting['all records'].items():
    print(f'sensor: {sensor}\nvalue: {value}')
    print(f'Device# {sensor} temperature is: {value["temperature"]}')
print(f'Humidity is: {get_humidity()}')
main_data_gathering_loop()
