"""A self contained and systemd service package for monitoring temperatures"""
__version__ = "0.1"
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from htr_readings import read_temperatures
from LCD_statusd import start_LCD_daemon
from loguru import logger
import time
from csv_functions import write_csv
from CONSTANTS import *


@logger.catch
def main_data_gathering_loop():
    while True:
        sensors_reporting = read_temperatures()
        logger.info(f"Updating readings of {len(sensors_reporting)} sensors...")
        write_csv(sensors_reporting)        
        logger.debug("Sleeping 1 second...")
        time.sleep(1)
    return


@logger.catch
def main():
    # TODO make a seperate script webserver that displays all details and offers ability to rename sensors
    logger.info("Start main recorder.")
    sensors_reporting = read_temperatures()
    logger.debug(f"sensors reporting:{sensors_reporting}")
    if sensors_reporting == []:
        # TODO log error
        logger.info("no sensors error")
    else:
        logger.info(f"{time_now_string()} ::: {len(sensors_reporting)} sensors found.")

    # TODO see if these next 2 functions can be runtogether by some means of multitasking.
    start_LCD_daemon()  # this function currently exits quickly and never runs again
    main_data_gathering_loop()  # process stays here until crash or reboot
    return


if __name__ == "__main__":
    main()
