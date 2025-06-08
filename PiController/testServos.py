import PiController

pi = PiController.PiController(18,19,2,3)

pi.assignPins()

try:
    while True:
        angle1 = int(input("Enter angle for Servo 1 (0-180): "))
        angle2 = int(input("Enter angle for Servo 2 (60-120): "))
        if 0 <= angle1 <= 180 and 0 <= angle2 <= 180:
            pi.setXAngle(angle1)
            pi.setYAngle(angle2)
        else:
            print("Angles must be between 0 and 180.")

except KeyboardInterrupt:
    print("\nExiting...")

finally:
    pi.end()
