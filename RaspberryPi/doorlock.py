import time
import LCD
import embedded

LIGHT_PIN = 4
SERVO_PIN = 18
BUZZER_PIN = 16

# Doorlock class
class DoorLock:
    # Doorlock setting (servo motor, photo resistor, buzzer)
    def __init__(self):
        self.isLock = True
        self.error_count = 0
        self.start_time = time.time()

        self.servo = embedded.Servo(SERVO_PIN)
        self.light = embedded.PhotoResistor(LIGHT_PIN, self)
        self.buzzer = embedded.Buzzer(BUZZER_PIN)
        self.reset()

    # Doorlock open
    def open(self, name=None):
        if name:
            LCD.print_face_unlock_correct(name)
        else:
            LCD.print_doorlock_open()
        self.isLock = False
        self.servo.turn(0)
        time.sleep(1)
        freq_list = [2000, 2250, 2660]
        self.buzzer.buzz(freq_list, 0.3, 1)
        self.error_count = 0

    # Doorlock close
    def close(self):
        LCD.print_doorlock_close()
        self.isLock = True
        self.servo.turn(90)
        freq_list = [2660, 2250, 2000]
        self.buzzer.buzz(freq_list, 0.3, 1)
        time.sleep(3)
        LCD.print_main()
        
    # Doorlock incorrect
    def incorrect(self, type):
        self.error_count += 1
        if self.error_count < 3:
            if type == "Unrecognized":
                LCD.print_face_unlock_incorrect()
            elif type == "Unrecognizable":
                LCD.print_face_unlock_unrecognizable()
            elif type == "Password":
                LCD.print_password_incorrect()
            freq_list = [2660, 0]
            self.buzzer.buzz(freq_list, 0.3, 3)
            LCD.print_main()
        else:
            self.warning()

    # Doorlock warning
    def warning(self):
        LCD.print_warning()
        self.error_count = 0
        freq_list = list(range(2000, 2660))
        self.buzzer.buzz(freq_list, 0.004, 5)
        time.sleep(30)
        LCD.print_main()

    # Doorlock reset
    def reset(self):
        LCD.print_waiting()
        self.error_count = 0
        self.isLock = True
        self.servo.turn(0)
