"""A self contained and systemd service package for monitoring temperatures"""
__version__ = "0.1"
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from w1Therm import read_temperatures
from dht11_test import get_humidity
from LCD_statusd import start_LCD_daemon
from open_weather_map import get_temp_and_humidity
from rotate_csv_and_compress import compress_local_csv
from loguru import logger
import time
from csv_functions import write_csv
from CONSTANTS import *


@logger.catch
def main_data_gathering_loop():
    time_delay = 0
    sensors_reporting = read_temperatures()
    print(sensors_reporting)
    while True:
        # TODO Compress_CSV_files() # CSV files need to be compressed periodically
        compress_local_csv()
        # TODO call this routine only twice a day (just in case one call fails)
        sensors_reporting = read_temperatures()
        write_csv(sensors_reporting["all records"])
        if time_delay >= 14:
            time_delay = 0
            # send_to_thingspeak(latest readings)
            # get current temp and humidity
            t, h = get_temp_and_humidity(ZIPCODE)
            pass
        print("Sleeping 1 second...")
        time_delay = +1
        time.sleep(1)
    return


@logger.catch
def main():
    # TODO make a seperate script webserver that displays all details and offers ability to rename sensors
    # TODO find a way to make IP address discoverable without attaching a monitor to the pi
    # TODO maybe use a common name that can be typed into a web browser on the same intranet
    print('Start main recorder.')
    sensors_reporting = read_temperatures()
    print(f"sensors reporting:\n{sensors_reporting}")
    if (sensors_reporting["all records"] == None) or (sensors_reporting["all records"] == {}):
        # TODO log error
        print('no sensors error')
    else:
        for sensor, value in sensors_reporting["all records"].items():
            print(f"sensor: {sensor}\nvalue: {value}")
            print(f'Device# {sensor} temperature is: {value["temperature"]}')

    print(f"Humidity is: {get_humidity()}")

    # temp_openweather, humidity_openweather = get_temp_and_humidity(ZIPCODE)

    # TODO see if these next 2 functions can be runtogether by some means of multitasking.
    start_LCD_daemon() # this function currently exits quickly and never runs again
    main_data_gathering_loop() # process stays here until crash or reboot
    return


if __name__ == "__main__":
    main()
