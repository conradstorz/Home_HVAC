# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

"""Simple test for I2C RGB character LCD shield kit"""
import time
import board
import adafruit_character_lcd.character_lcd_rgb_i2c as character_lcd

# Modify this if you have a different sized Character LCD
LCD_COLUMNS = 16
LCD_ROWS = 2
RED_BACKLIGHT = [100, 0, 0]
BLUE_BACKLIGHT = [0, 100, 0]
GREEN_BACKLIGHT = [0, 0, 100]
PURPLE_BACKLIGHT = [50, 0, 50]
BACKLIGHT_OFF = [0, 0, 0]
WELCOME_MESSAGE = "Hello\nCircuitPython"
EXIT_MESSAGE = "Going to sleep\nCya later!"

# Initialise I2C bus.
i2c = board.I2C()  # uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller

# Initialise the LCD class
lcd = character_lcd.Character_LCD_RGB_I2C(i2c, LCD_COLUMNS, LCD_ROWS)


def lcd_exercise():
    """Perform some show-off displays"""
    lcd.clear()
    # Set LCD color to red
    lcd.color = RED_BACKLIGHT
    time.sleep(1)
    # Print two line message
    lcd.message = WELCOME_MESSAGE
    # Wait 5s
    time.sleep(5)
    # Set LCD color to blue
    lcd.color = BLUE_BACKLIGHT
    time.sleep(1)
    # Set LCD color to green
    lcd.color = GREEN_BACKLIGHT
    time.sleep(1)
    # Set LCD color to purple
    lcd.color = PURPLE_BACKLIGHT
    time.sleep(1)
    lcd.clear()
    # Print two line message right to left
    lcd.text_direction = lcd.RIGHT_TO_LEFT
    lcd.message = WELCOME_MESSAGE
    # Wait 5s
    time.sleep(5)
    # Return text direction to left to right
    lcd.text_direction = lcd.LEFT_TO_RIGHT
    # Display cursor
    lcd.clear()
    lcd.cursor = True
    lcd.message = "Cursor! "
    # Wait 5s
    time.sleep(5)
    # Display blinking cursor
    lcd.clear()
    lcd.blink = True
    lcd.message = "Blinky Cursor!"
    # Wait 5s
    time.sleep(5)
    lcd.blink = False
    lcd.clear()
    # Create message to scroll
    scroll_msg = "<-- Scroll"
    lcd.message = scroll_msg
    # Scroll to the left
    for i in range(len(scroll_msg)):
        time.sleep(0.5)
        lcd.move_left()
    lcd.clear()
    time.sleep(1)
    lcd.message = EXIT_MESSAGE
    time.sleep(5)
    # Turn off LCD backlights and clear text
    lcd.color = BACKLIGHT_OFF
    lcd.clear()
    return


def scrolling_message(message, recycle=True, color=BLUE_BACKLIGHT):
    """Display a scrolling message in BLUE by default and recycle endlessly"""
    lcd.clear()
    lcd.color = color
    while True:
        lcd.message = message
        # Scroll to the left
        for i in range(len(message)):
            time.sleep(0.5)
            lcd.move_left()
        lcd.clear()
        time.sleep(0.5)
        if recycle != True:
            break
    return


def static_message(message, color=BLUE_BACKLIGHT):
    """Display a static message and return"""
    lcd.clear()
    lcd.color = color
    lcd.message = message
    return


if __name__ == "__main__":
    while True:
        lcd_exercise()
