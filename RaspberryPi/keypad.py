# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT
import time
import digitalio
import board
import adafruit_matrixkeypad

# Membrane 3x4 matrix keypad on Raspberry Pi -
# https://www.adafruit.com/product/419
cols = [digitalio.DigitalInOut(x) for x in (board.D8, board.D7, board.D1)]
rows = [digitalio.DigitalInOut(x) for x in (board.D6, board.D13, board.D19, board.D26)]

keys = ((1, 2, 3), (4, 5, 6), (7, 8, 9), ("*", 0, "#"))
keypad = adafruit_matrixkeypad.Matrix_Keypad(rows, cols, keys)
doorlock_password = "2023"

# Check & Print password
def password(LCD_module, doorlock):
    entered_password = ""
    start_time = time.time()
    while True:
        unrecognizable_time = time.time() - start_time
        if unrecognizable_time > 10:
            break
        keys = keypad.pressed_keys
        if keys:
            doorlock.buzzer.buzz([2000], 0.2, 1)
            if keys[0] == "#":
                if entered_password == doorlock_password:
                    print("Correct password!\n")
                    doorlock.open()
                else:
                    print("Incorrect password!\n")
                    doorlock.incorrect("Password")
                break
            else:
                entered_password += str(keys[0])
                LCD_module.printout("*")
        time.sleep(0.1)

# Check & Print call room
def call(LCD_module, doorlock, user_data):
    entered_host = ""
    start_time = time.time()
    while True:
        unrecognizable_time = time.time() - start_time
        if unrecognizable_time > 10:
            break
        keys = keypad.pressed_keys
        if keys:
            doorlock.buzzer.buzz([2000], 0.1, 1)
            if keys[0] == "#":
                found_users = user_data.search_users_by_info("Room", entered_host)
                if found_users:
                    print("Calling host...\n")
                    return found_users
                else:
                    print("Host not found.\n")
                    return None
            else:
                entered_host += str(keys[0])
                LCD_module.printout(keys[0])
        time.sleep(0.1)

# Press "*" to main screen
def main_button(wait_time):
    start_time = time.time()
    while True:
        unrecognizable_time = time.time() - start_time
        if unrecognizable_time > wait_time:
            break
        keys = keypad.pressed_keys
        if keys:
            if keys[0] == "*":
                break
