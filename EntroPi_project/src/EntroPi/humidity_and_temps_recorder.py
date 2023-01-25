"""A self contained and systemd service package for monitoring temperatures"""
__version__ = "0.1"
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from w1Therm import read_temperatures
from dht11_test import get_humidity
from LCD_statusd import start_LCD_daemon
from weather_underground import get_temp_and_humidity
from rotate_csv_and_compress import compress_local_csv
from loguru import logger
from datetime import datetime
import time
import csv
from os import path

ZIPCODE = "47119"
BASENAME_CSV_FILE = '_HVAC_temps'

def generate_csv_filename(basename = None):
    if basename == None:
        basename = BASENAME_CSV_FILE
    return f'{datetime.now().strftime("%Y%m%d")}{basename}.csv'

@logger.catch
def write_csv(device_data, directory="."):
    # Open the output CSV file and write 'the results
    print(f"\ndevice_data:\n{device_data}\n")
    if device_data != None:
        if device_data != {}:
            first_key = list(device_data)[0]
            # print(f'first key: {first_key}')
            first_device_values = device_data[first_key]
            fieldnames = first_device_values.keys()  # retrieve keys from nested dictionaries
            print(f"\nfilednames:\n{fieldnames}\n")
            out_csv = generate_csv_filename()
            # check if file exists and write headers if new file
            if not path.exists(out_csv):
                with open(out_csv, "w", newline="") as h:
                    writer = csv.DictWriter(h, fieldnames=fieldnames)
                    writer.writeheader()
            else:
                with open(out_csv, "a", newline="") as h:
                    writer = csv.DictWriter(h, fieldnames=fieldnames)
                    # Write a row for each location
                    for device, values in device_data.items():
                        writer.writerow(values)
            print(f"Output file saved as {out_csv}.")
        else:
            # TODO log error
            print('Empty dict unexpected.')
    else:
        # TODO log error
        print('No data to add to CSV file.')
    return


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
