"""A self contained and systemd service package for monitoring temperatures"""
__version__ = "0.1"
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta, time, date
from w1Therm import read_temperatures, time_now_string
from dht11_test import get_humidity
from LCD_statusd import start_LCD_daemon

from loguru import logger
import time
from csv_functions import write_csv
from CONSTANTS import *


@logger.catch
def main_data_gathering_loop():
    while True:
        sensors_reporting = read_temperatures()
        print(f"{time_now_string()} Updating readings of {len(sensors_reporting['responding'])} sensors...")
        # TODO add local weather conditions to CSV output
        # TODO add indoor humidity to CSV report
        write_csv(sensors_reporting["all records"])        
        # print("Sleeping 1 second...")
        time.sleep(1)
    return


@logger.catch
def main():
    # TODO make a seperate script webserver that displays all details and offers ability to rename sensors
    print("Start main recorder.")
    sensors_reporting = read_temperatures()
    # print(f"\nsensors reporting:\n{sensors_reporting}")
    error = True
    if (sensors_reporting != None):
        if (sensors_reporting["all records"] != {}):
            if (sensors_reporting["all records"] != None):
                print(f"{time_now_string()} ::: {len(sensors_reporting['responding'])} sensors found.")
                error = False
    if error:
        # TODO log error
        print("no sensors error")

    # TODO see if these next 2 functions can be runtogether by some means of multitasking.
    start_LCD_daemon()  # this function currently exits quickly and never runs again
    main_data_gathering_loop()  # process stays here until crash or reboot
    return


if __name__ == "__main__":
    main()
