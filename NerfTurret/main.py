import os
import sys
import threading
import numpy as np

from Camera import Camera
from PiController import PiController
from Turret import Turret

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


X_SERVO_PIN = 18
Y_SERVO_PIN = 19
CHARGE_PIN = 2
SHOOT_PIN = 3
running = True
counter = 0

def wait_for_exit():
    global running
    input("Press [Enter] to exit...\n")
    running = False

args = sys.argv[1:]
if len(args) == 3 and args[2] == '-onPi':
    print_iteration = int(args[0])
    target_class = args[1]
    running_on_pi = True
elif len(args) == 2:
    print_iteration = int(args[0])
    target_class = args[1]
    running_on_pi = False
elif len(args) == 1:
    print_iteration = int(args[0])
    target_class = 'person'
    running_on_pi = False
else:
    print_iteration = 5
    target_class = 'person'
    running_on_pi = False

print(print_iteration, target_class, running_on_pi)
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