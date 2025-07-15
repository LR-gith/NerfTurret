import os
import time

from dotenv import load_dotenv

try:
    import RPi.GPIO as GPIO

    running_on_pi = True
except (ImportError, RuntimeError):
    GPIO = None
    running_on_pi = False

env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(env_path)
X_SERVO_PIN = int(os.getenv('X_SERVO_PIN'))
Y_SERVO_PIN = int(os.getenv('Y_SERVO_PIN'))
CHARGE_PIN = int(os.getenv('CHARGE_PIN'))
LOAD_PIN = int(os.getenv('LOAD_PIN'))


class PiController:

    def __init__(self, verbose=False):
        self.x_servo_angle = 90
        self.y_servo_angle = 90
        self.x_servo = None
        self.y_servo = None
        self.x_servo_pin = X_SERVO_PIN
        self.y_servo_pin = Y_SERVO_PIN
        self.charge_pin = CHARGE_PIN
        self.load_pin = LOAD_PIN
        self.verbose = verbose
        self._assign_pins()


    def shoot(self, charge_time, load_time):
        if not running_on_pi:
            return
        if charge_time not in range(0, 6) or load_time not in range(0, 6):
            raise ValueError("Invalid charge- or load-time")
        GPIO.output(self.charge_pin, GPIO.HIGH)
        time.sleep(charge_time)
        GPIO.output(self.load_pin, GPIO.HIGH)
        time.sleep(load_time)
        GPIO.output(self.charge_pin, GPIO.LOW)
        GPIO.output(self.load_pin, GPIO.LOW)
        if self.verbose: print("Shot one time")


    def charge(self, waittime):
        if not running_on_pi:
            return
        if waittime not in range(0, 6):
            raise ValueError("Invalid charge time")
        GPIO.output(self.charge_pin, GPIO.HIGH)
        time.sleep(waittime)
        GPIO.output(self.charge_pin, GPIO.LOW)
        if self.verbose: print("Charged for", waittime, "seconds")


    def load(self, waittime):
        if not running_on_pi:
            return
        if waittime not in range(0, 6):
            raise ValueError("Invalid load time")
        GPIO.output(self.load_pin, GPIO.HIGH)
        time.sleep(waittime)
        GPIO.output(self.load_pin, GPIO.LOW)
        if self.verbose: print("Loaded for", waittime, "seconds")


    def default_servo_position(self):
        self.x_servo_angle = 90
        self._set_x_angle(90)
        self.y_servo_angle = 90
        self._set_y_angle(90)


    def align(self, relative_x_angle, relative_y_angle):
        self.x_servo_angle += relative_x_angle
        self.y_servo_angle += relative_y_angle
        if self.verbose: print("Moving servo ", relative_x_angle, "in x to pos",
                               self.x_servo_angle)
        self._set_x_angle(self.x_servo_angle)
        if self.verbose: print("Moving servo ", relative_y_angle, "in y to pos",
                               self.y_servo_angle)
        self._set_y_angle(self.y_servo_angle)


    def _assign_pins(self):
        if not running_on_pi:
            if self.verbose: print("No servos moved because not running on Pi")
            return
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.x_servo_pin, GPIO.OUT)
        self.x_servo = GPIO.PWM(self.x_servo_pin, 50)
        self.x_servo.start(0)
        GPIO.setup(self.y_servo_pin, GPIO.OUT)
        self.y_servo = GPIO.PWM(self.y_servo_pin, 50)
        self.y_servo.start(0)
        GPIO.setup(self.charge_pin, GPIO.OUT)
        GPIO.setup(self.load_pin, GPIO.OUT)


    def _set_x_angle(self, angle):
        if 0 <= angle <= 180:
            self._set_angle(self.x_servo, angle)
            self.x_servo_angle = angle
        elif angle < 0:
            self.x_servo_angle = 0
            self._set_angle(self.x_servo, 0)
            if self.verbose: print("Invalid angle for the xServo, moved to 0")
        elif 180 < angle:
            self.x_servo_angle = 180
            self._set_angle(self.x_servo, 180)
            if self.verbose: print("Invalid angle for the xServo, moved to 180")


    def _set_y_angle(self, angle):
        if 60 <= angle <= 120:
            self._set_angle(self.y_servo, angle)
            self.y_servo_angle = angle
        elif angle < 60:
            self.y_servo_angle = 60
            self._set_angle(self.x_servo, 60)
            if self.verbose: print("Invalid angle for the xServo, moved to 60")
        elif 120 < angle:
            self.y_servo_angle = 120
            self._set_angle(self.x_servo, 120)
            if self.verbose: print("Invalid angle for the xServo, moved to 120")


    def _set_angle(self, servo, angle):
        if not running_on_pi:
            if self.verbose: print("No servos moved because not running on Pi")
            return
        duty = angle / 18 + 2
        servo.ChangeDutyCycle(duty)
        time.sleep(0.5)
        servo.ChangeDutyCycle(0)


    def get_x_servo_angle(self) -> int:
        return self.x_servo_angle


    def get_y_servo_angle(self) -> int:
        return self.y_servo_angle


    def stop(self):
        if running_on_pi:
            self.x_servo.stop()
            self.y_servo.stop()
            GPIO.cleanup()
