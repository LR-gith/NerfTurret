import threading
import numpy as np
import argparse

from Camera import Camera
from PiController import PiController
from Turret import Turret


X_SERVO_PIN = 18
Y_SERVO_PIN = 19
CHARGE_PIN = 2
SHOOT_PIN = 3
running = True
counter = 0


parser = argparse.ArgumentParser()
parser.add_argument("-i", "--iteration", type=int, help="output after I iterations", default=5)
parser.add_argument("-c", "--class", type=str, help="detects this object class C", default="person", dest="targetClass")
parser.add_argument("-pi", "--runningOnPi", action="store_true", help="Use when running the code on a pi")
args = parser.parse_args()


def wait_for_exit():
    global running
    input("Press [Enter] to exit...\n")
    running = False

print_iteration = args.iteration
target_class = args.targetClass
running_on_pi = args.runningOnPi

print("iteration: %d, class: %s, pi: %b",print_iteration, target_class, running_on_pi)
controller = None
if running_on_pi: controller = PiController(X_SERVO_PIN, Y_SERVO_PIN, CHARGE_PIN, SHOOT_PIN)
camera = Camera(1)
turret = Turret(controller, camera, target_class,running_on_pi=running_on_pi)

exit_thread = threading.Thread(target=wait_for_exit, daemon=True)
exit_thread.start()

while running:
    confidence, x_angle, y_angle = turret.run()

    if counter % print_iteration == 0:
        if confidence == -1:
            print("Detected no", target_class)
        else:
            print("Detected", target_class, " With confidence:", np.round(confidence, 3))
            print("x:   ", x_angle, "    y:  ", y_angle)

    counter += 1

turret.stop()
camera.stop()
if running_on_pi: controller.stop()



#76,100 auf 100cm
#auf breite 70°
#auf höhe 90°