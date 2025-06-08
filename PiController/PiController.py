import RPi.GPIO as GPIO
import time

class PiController:

    def __init__(self, xServoPin, yServoPin, chargePin, shootPin):
        self.xServo = None
        self.yServo = None
        self.xServoPin = xServoPin
        self.yServoPin = yServoPin
        self.chargePin = chargePin
        self.shootPin = shootPin

    def assignPins(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.xServoPin, GPIO.OUT)
        self.xServo = GPIO.PWM(self.xServoPin, 50)
        self.xServo.start(0)
        GPIO.setup(self.yServoPin, GPIO.OUT)
        self.yServo = GPIO.PWM(self.yServoPin, 50)
        self.yServo.start(0)
        GPIO.setup(self.chargePin, GPIO.OUT)
        GPIO.setup(self.shootPin, GPIO.OUT)

    def shoot(self):
        GPIO.output(self.chargePin, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(self.shootPin, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(self.chargePin, GPIO.LOW)
        GPIO.output(self.shootPin, GPIO.LOW)
        print("Shot one time")

    def charge(self,time):
        GPIO.output(self.chargePin, GPIO.HIGH)
        time.sleep(time)
        GPIO.output(self.chargePin, GPIO.LOW)
        print("Charged for", time, "seconds")

    def load(self, time):
        GPIO.output(self.shootPin, GPIO.HIGH)
        time.sleep(time)
        GPIO.output(self.shootPin, GPIO.LOW)
        print("Loaded for", time, "seconds")


    def defaultServosPos(self):
        self.setXAngle(90)
        self.setYAngle(90)

    def align(self,xAngle, yAngle):
        print("To be implemented")


    def setXAngle(self, angle):
        if 0 <= angle <= 180:
            self.setAngle(self.xServo, angle)
        else:
            print("Invalid angle for the xServo")

    def setYAngle(self, angle):
        if 60 <= angle <= 120:
            self.setAngle(self.yServo, angle)
        else:
            print("Invalid angle for the yServo")

    def setAngle(self, servo, angle):
        duty = angle / 18 + 2
        servo.ChangeDutyCycle(duty)
        time.sleep(0.5)
        servo.ChangeDutyCycle(0)

    def end(self):
        self.xServo.stop()
        self.yServo.stop()
        GPIO.cleanup()