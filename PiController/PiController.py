import RPi.GPIO as GPIO
import time

class PiController:

    def __init__(self, xServoPin, yServoPin, chargePin, shootPin):
        self.xServoPin = xServoPin
        self.yServoPin = yServoPin
        self.chargePin = chargePin
        self.shootPin = shootPin

    def assignPins(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.xServoPin, GPIO.out)
        GPIO.setup(self.yServoPin, GPIO.out)
        GPIO.setup(self.chargePin, GPIO.out)
        GPIO.setup(self.shootPin, GPIO.out)

    def shoot(self):
        GPIO.output(self.chargePin, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(self.shootPin, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(self.chargePin, GPIO.LOW)
        GPIO.output(self.shootPin, GPIO.LOW)
        print("Shot one time")