import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.turret.pi_controller import PiController

controller = PiController(verbose=True)

try:
    while True:
        x_angle = int(input("Enter angle for servo x (0-180): "))
        y_angle = int(input("Enter angle for servo y (70-110): "))
        if 0 <= x_angle <= 180 and 0 <= y_angle <= 180:
            controller._set_x_angle(x_angle)
            controller._set_y_angle(y_angle)
        else:
            print("Angles must be between 0 and 180.")

except KeyboardInterrupt:
    print("\nExiting...")

finally:
    controller.stop()
