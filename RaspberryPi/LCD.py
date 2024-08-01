import sys
import time
import keypad
import user_data
import rgb1602
import RPi.GPIO as GPIO

# System path
sys.path.append('../')

# Define pin
CALL_PIN        = 22
PASSWORD_PIN    = 5
RECOGNITION_PIN = 27

# Define LCD Background Color
COLOR_R = 100
COLOR_G = 100
COLOR_B = 100

# Define keys
lcd_key         = 0
btn_call        = "Call"
btn_password    = "Password"
btn_recognition = "Recognition"

# Define GPIO
GPIO.setup(CALL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(PASSWORD_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(RECOGNITION_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Setting LCD
lcd=rgb1602.RGB1602(16,2)
lcd.setRGB(COLOR_R, COLOR_G, COLOR_B)
GPIO.setmode(GPIO.BCM)
    

# Print waiting (before doorlock start)
def print_waiting():
    lcd.clear()
    lcd.setCursor(0, 0)
    lcd.printout("Waiting...")

# Print recognizing (face recognizing)
def print_recognizing():
    lcd.clear()
    lcd.setCursor(0, 0)
    lcd.printout("Recognizing...")
    lcd.setCursor(0, 1)
    lcd.printout("Wait a second...")

# Print doorlock open (match face information)
def print_face_unlock_correct(name):
    lcd.clear()
    lcd.setCursor(0, 0)
    lcd.printout(name)
    lcd.setCursor(0, 1)
    lcd.printout("Welcome!")

# Print doorlock incorrect (mismatch face information)
def print_face_unlock_incorrect():
    lcd.clear()
    lcd.setCursor(0, 0)
    lcd.printout("No matching")
    lcd.setCursor(0, 1)
    lcd.printout("information")

# Print unrecognizable (unrecognizable face)
def print_face_unlock_unrecognizable():
    lcd.clear()
    lcd.setCursor(0, 0)
    lcd.printout("Unrecognizable!!")
    lcd.setCursor(0, 1)
    lcd.printout("Please try again")

# Print password field
def print_password():
    lcd.clear()
    lcd.setCursor(0, 0)
    lcd.printout("Password")
    lcd.setCursor(0, 1)
    lcd.printout("-> ")

# Print password incorrect (mismatch password)
def print_password_incorrect():
    lcd.clear()
    lcd.setCursor(0, 0)
    lcd.printout("Password")
    lcd.setCursor(0, 1)
    lcd.printout("incorrect")

# Print warning (error occurred 3 times)
def print_warning():
    lcd.clear()
    lcd.setCursor(0, 0)
    lcd.printout("Warning!")
    lcd.setCursor(0, 1)
    lcd.printout("Incorrect 3times")

# Print call field
def print_call():
    lcd.clear()
    lcd.setCursor(0, 0)
    lcd.printout("Enter button = #")
    lcd.setCursor(0, 1)
    lcd.printout("Call: ")

# Print calling host (resident call)
def print_calling_host():
    lcd.clear()
    lcd.setCursor(0, 0)
    lcd.printout("Calling host...")
    lcd.setCursor(0, 1)
    lcd.printout("Back button = *")

# Print call error (wrong resident information)
def print_call_error():
    lcd.clear()
    lcd.setCursor(0, 0)
    lcd.printout("Invalid host...")
    lcd.setCursor(0, 1)
    lcd.printout("Please try again")

# Print doorlock open
def print_doorlock_open():
    lcd.clear()
    lcd.setCursor(0, 0)
    lcd.printout("Doorlock open!")
    lcd.setCursor(0, 1)
    lcd.printout("Welcome!")

# Print doorlock close
def print_doorlock_close():
    lcd.clear()
    lcd.setCursor(0, 0)
    lcd.printout("The doorlock")
    lcd.setCursor(0, 1)
    lcd.printout("is locked!")


# Print main (select menu)
def print_main():
    lcd.clear()
    lcd.setCursor(0, 0)
    lcd.printout("1)Password     ")
    lcd.setCursor(0, 1)
    lcd.printout("2)Face   3)Call")

# Password function (1. password button)
def password(doorlock):
    print_password()
    keypad.password(lcd, doorlock)
    print_main()

# Face Unlock function (2. face button)
def face_unlock(face, doorlock):
    print_recognizing()
    face.face_recognition(doorlock)

# Call function (3. call button)
def call(server, face, doorlock):
    print_call()
    found_users = keypad.call(lcd, doorlock, user_data)

    if found_users:
        print_calling_host()
        for user in found_users:
            server.knock_knock(user)
            face.guest_face()
        keypad.main_button(30)
        print_main()
    else:
        print_call_error()
        time.sleep(3)
    print_main()

# Read the key value
def read_LCD_buttons():
    key_call = GPIO.input(CALL_PIN)
    key_password = GPIO.input(PASSWORD_PIN)
    key_recognition = GPIO.input(RECOGNITION_PIN)

    if (key_call == 1):
        return btn_call
    if (key_password == 1):
        return btn_password
    if (key_recognition == 1):
        return btn_recognition

# Main LCD function
def start_doorlock(server, face_module, doorlock):
    while True:
        if doorlock.isLock:
            lcd_key = read_LCD_buttons()
            time.sleep(0.1)
            lcd_key = read_LCD_buttons()
            if lcd_key == btn_password:
                password(doorlock)
            elif lcd_key == btn_call:
                call(server, face_module, doorlock)
            elif lcd_key == btn_recognition:
                face_unlock(face_module, doorlock)
        else:
            light = doorlock.light.rc_time()
            if light > 50000:
                doorlock.close()
