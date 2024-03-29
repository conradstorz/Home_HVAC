"""Initialize LCD module and display status.
local IP address
Number of devices online
"""


"""
from subprocess import check_output
lcd.message('Local IP Address:\n')
lcd.message(ips2 = check_output(['hostname', '--all-ip-addresses']).decode('utf-8'))

read JSON file that has IDs and locations and last seen info
determine how many devices are currently active
active_devices = 0
"""
import time
import board
from CONSTANTS import *
from subprocess import check_output
import adafruit_character_lcd.character_lcd_rgb_i2c as character_lcd
from loguru import logger

# These values are specific to the hardware attached so are not included in the CONSTANTS file
# Modify this if you have a different sized Character LCD
LCD_COLUMNS = 16
LCD_ROWS = 2
RED_BACKLIGHT = [100, 0, 0]
BLUE_BACKLIGHT = [0, 0, 100]
GREEN_BACKLIGHT = [0, 100, 0]
PURPLE_BACKLIGHT = [50, 0, 50]
BACKLIGHT_OFF = [0, 0, 0]


# Initialise I2C bus.
i2c = board.I2C()  # uses board.SCL and board.SDA

# Initialise the LCD class
lcd = character_lcd.Character_LCD_RGB_I2C(i2c, LCD_COLUMNS, LCD_ROWS)


@logger.catch
def start_LCD_daemon():
    """Periodically update attached LCD with details of running program.
    This code exits quickly but could be long running if it is compatible
    with some type of hypervisor multitasking scheme."""
    # TODO add monitoring of internet availability and log status
    logger.info("Start LCD update.")
    lcd.clear()
    # Set LCD color to red
    lcd.color = RED_BACKLIGHT
    # Print two line message
    lcd.message = WELCOME_MESSAGE
    time.sleep(0.2)
    lcd.clear()
    lcd.message = "IP Address\nUNKNOWN"
    time.sleep(1)
    ips2 = check_output(["hostname", "--all-ip-addresses"]).decode("utf-8").split()
    # TODO check that IP address is valid
    logger.info(f"IP address lookup: {ips2}")
    lcd.clear()
    # Set LCD color to red
    lcd.color = GREEN_BACKLIGHT
    # Print two line message
    if len(ips2) > 0:
        ip1 = ips2[0]
    else:
        ip1 = "None"
    if len(ips2) > 1:
        ip2 = ips2[1]
    else:
        ip2 = "n/a"
    lcd.message = f"IP1:{ip1}\nIP2:{ip2}"
    return
