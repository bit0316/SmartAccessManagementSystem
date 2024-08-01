import time
import pigpio
import RPi.GPIO as GPIO

# Servo motor class
class Servo:
    # Servo motor setting
    def __init__(self, pin):
        self.pi = pigpio.pi()
        self.pin = pin
        self.pi.set_mode(self.pin, pigpio.OUTPUT)
        self.pi.set_servo_pulsewidth(self.pin, 500)
    
    # Servo motor rotation
    def turn(self, angle):
        pulsewidth = (angle / 180 * (2500 - 500)) + 500
        self.pi.set_servo_pulsewidth(self.pin, pulsewidth)

    # Servo motor stop    
    def stop(self):
        self.pi.stop()

# Piezo buzzer class
class Buzzer:
    # Piezo buzzer setting
    def __init__(self, pin):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        self.buzzer = GPIO.PWM(self.pin, 1000)
        GPIO.setwarnings(False)
    
    # Piezo buzzer sound output
    def buzz(self, freq_list, duration, repeat):
        self.buzzer.start(0)
        for _ in range(repeat):
            for freq in freq_list:
                if freq == 0:
                    time.sleep(duration)
                else:
                    self.buzzer.ChangeFrequency(freq)
                    self.buzzer.ChangeDutyCycle(10)
                    time.sleep(duration)
                    self.buzzer.ChangeDutyCycle(0)
        self.buzzer.stop()

    # Piezo buzzer stop    
    def stop(self):
        GPIO.cleanup()

# Photo resistor class
class PhotoResistor:
    # Photo resistor setting
    def __init__(self, pin):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN)
        GPIO.setwarnings(False)

    # Photo resistor measures
    def rc_time(self):
        count = 0
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.LOW)
        time.sleep(0.1)
        GPIO.setup(self.pin, GPIO.IN)
        while (GPIO.input(self.pin) == GPIO.LOW):
            count += 1
        return count

    # Photo resistor stop
    def stop(self):
        GPIO.cleanup()
