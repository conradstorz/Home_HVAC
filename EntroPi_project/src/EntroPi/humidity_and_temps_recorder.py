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
        print(f"{time_now_string()} Updating readings of {len(sensors_reporting)} sensors...")
        write_csv(sensors_reporting)        
        # print("Sleeping 1 second...")
        time.sleep(1)
    return


@logger.catch
def main():
    # TODO make a seperate script webserver that displays all details and offers ability to rename sensors
    print("Start main recorder.")
    sensors_reporting = read_temperatures()
    # print(f"\nsensors reporting:\n{sensors_reporting}")
    if sensors_reporting == []:
        # TODO log error
        print("no sensors error")
    else:
        print(f"{time_now_string()} ::: {len(sensors_reporting)} sensors found.")

    # TODO see if these next 2 functions can be runtogether by some means of multitasking.
    start_LCD_daemon()  # this function currently exits quickly and never runs again
    main_data_gathering_loop()  # process stays here until crash or reboot
    return


if __name__ == "__main__":
    main()
