import time
import Client

try:
    import RPi.GPIO as GPIO
    running_on_pi = True
except (ImportError, RuntimeError):
    Client.log_to_server("Turret isn't operating on pi!")
    Client.log_to_server("No GPIO output will be done!")
    GPIO = None
    running_on_pi = False


class PiController:

    def __init__(self, xServoPin, yServoPin, chargePin, shootPin):
        self.xServoAngle = 90
        self.yServoAngle = 90
        self.xServo = None
        self.yServo = None
        self.xServoPin = xServoPin
        self.yServoPin = yServoPin
        self.chargePin = chargePin
        self.shootPin = shootPin
        self.__assignPins()

    def shoot(self):
        if not running_on_pi:
            return
        GPIO.output(self.chargePin, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(self.shootPin, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(self.chargePin, GPIO.LOW)
        GPIO.output(self.shootPin, GPIO.LOW)
        print("Shot one time")

    def charge(self, waittime):
        if not running_on_pi:
            return
        GPIO.output(self.chargePin, GPIO.HIGH)
        time.sleep(waittime)
        GPIO.output(self.chargePin, GPIO.LOW)
        print("Charged for", waittime, "seconds")

    def load(self, waittime):
        if not running_on_pi:
            return
        GPIO.output(self.shootPin, GPIO.HIGH)
        time.sleep(waittime)
        GPIO.output(self.shootPin, GPIO.LOW)
        print("Loaded for", waittime, "seconds")

    def defaultServoPosition(self):
        self.xServoAngle = 90
        self.__setXAngle(90)
        self.yServoAngle = 90
        self.__setYAngle(90)

    def align(self, xAngle, yAngle):
        self.xServoAngle += xAngle
        self.yServoAngle += yAngle
        print("Moving servo ", xAngle, "in x to pos", self.xServoAngle)
        self.__setXAngle(self.xServoAngle)
        print("Moving servo ", yAngle, "in y to pos", self.yServoAngle)
        self.__setYAngle(self.yServoAngle)

    def __assignPins(self):
        if not running_on_pi:
            print("No servos moved because not running on Pi")
            return
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.xServoPin, GPIO.OUT)
        self.xServo = GPIO.PWM(self.xServoPin, 50)
        self.xServo.start(0)
        GPIO.setup(self.yServoPin, GPIO.OUT)
        self.yServo = GPIO.PWM(self.yServoPin, 50)
        self.yServo.start(0)
        GPIO.setup(self.chargePin, GPIO.OUT)
        GPIO.setup(self.shootPin, GPIO.OUT)

    def __setXAngle(self, angle):
        if 0 <= angle <= 180:
            self.__setAngle(self.xServo, angle)
        elif angle < 0:
            self.xServoAngle = 0
            self.__setAngle(self.xServo, 0)
            print("Invalid angle for the xServo, moved to 0")
        elif 180 < angle:
            self.xServoAngle = 180
            self.__setAngle(self.xServo, 180)
            print("Invalid angle for the xServo, moved to 180")

    def __setYAngle(self, angle):
        if 60 <= angle <= 120:
            self.__setAngle(self.yServo, angle)
        elif angle < 60:
            self.yServoAngle = 60
            self.__setAngle(self.xServo, 60)
            print("Invalid angle for the xServo, moved to 60")
        elif 120 < angle:
            self.yServoAngle = 120
            self.__setAngle(self.xServo, 120)
            print("Invalid angle for the xServo, moved to 120")

    def __setAngle(self, servo, angle):
        if not running_on_pi:
            print("No servos moved because not running on Pi")
            return
        duty = angle / 18 + 2
        servo.ChangeDutyCycle(duty)
        time.sleep(0.5)
        servo.ChangeDutyCycle(0)

    def getXServoAngle(self):
        return self.xServoAngle

    def getYServoAngle(self):
        return self.yServoAngle

    def stop(self):
        if running_on_pi:
            self.xServo.stop()
            self.yServo.stop()
            GPIO.cleanup()
