#import RPi.GPIO as GPIO
import time


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
        GPIO.output(self.chargePin, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(self.shootPin, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(self.chargePin, GPIO.LOW)
        GPIO.output(self.shootPin, GPIO.LOW)
        print("Shot one time")

    def charge(self, waittime):
        GPIO.output(self.chargePin, GPIO.HIGH)
        time.sleep(waittime)
        GPIO.output(self.chargePin, GPIO.LOW)
        print("Charged for", waittime, "seconds")

    def load(self, waittime):
        GPIO.output(self.shootPin, GPIO.HIGH)
        time.sleep(waittime)
        GPIO.output(self.shootPin, GPIO.LOW)
        print("Loaded for", waittime, "seconds")

    def defaultServoPosition(self):
        self.__setXAngle(90)
        self.__setYAngle(90)

    def align(self, xAngle, yAngle):
        self.xServoAngle += xAngle
        self.yServoAngle += yAngle
        print("Moving servo ", xAngle, "in x to pos", self.xServoAngle)
        self.__setXAngle(self.xServoAngle)
        print("Moving servo ", yAngle, "in y to pos", self.yServoAngle)
        self.__setYAngle(self.yServoAngle)

    def __assignPins(self):
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
            self.__setAngle(self.xServo, 0)
            print("Invalid angle for the xServo")
        elif 180 < angle:
            self.__setAngle(self.xServo, 180)
            print("Invalid angle for the xServo")

    def __setYAngle(self, angle):
        if 60 <= angle <= 120:
            self.__setAngle(self.yServo, angle)
        elif angle < 60:
            self.__setAngle(self.xServo, 60)
            print("Invalid angle for the xServo")
        elif 120 < angle:
            self.__setAngle(self.xServo, 120)
            print("Invalid angle for the xServo")

    def __setAngle(self, servo, angle):
        duty = angle / 18 + 2
        servo.ChangeDutyCycle(duty)
        time.sleep(0.5)
        servo.ChangeDutyCycle(0)

    def stop(self):
        self.xServo.stop()
        self.yServo.stop()
        GPIO.cleanup()
