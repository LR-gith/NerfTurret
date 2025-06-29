import threading
import argparse
import Client

# initializes connection to the server
if not Client.initializeConnection():
    exit("Failed to connect to Server")

from Camera import Camera
from Turret import Turret
from PiController import PiController



X_SERVO_PIN = 18
Y_SERVO_PIN = 19
CHARGE_PIN = 2
SHOOT_PIN = 3
running = True
counter = 0


parser = argparse.ArgumentParser()
parser.add_argument("-i", "--iteration", type=int, help="output after I iterations", default=5)
parser.add_argument("-c", "--class", type=str, help="detects this object class C", default="person", dest="targetClass")
parser.add_argument("-img", "--showImg", action="store_true", help="When used an window will display the camera after detection")
args = parser.parse_args()


def wait_for_exit():
    global running
    input("Press [Enter] to exit...\n")
    running = False

print_iteration = args.iteration
target_class = args.targetClass
show_img = args.showImg

print("iteration: ",print_iteration , ", class: ",target_class ,", show image: ", show_img)


controller = PiController(X_SERVO_PIN, Y_SERVO_PIN, CHARGE_PIN, SHOOT_PIN)
camera = Camera(0)
turret = Turret(controller, camera, target_class, show_img=show_img)

exit_thread = threading.Thread(target=wait_for_exit, daemon=True)
exit_thread.start()

while running:
    frame, values = turret.run()
    confidence = values["conf"]
    Client.update_value_on_server(frame, values)

    if counter % print_iteration == 0:
        if confidence == -1:
            Client.log_to_server(f"No {target_class} detected")
        else:
            Client.log_to_server(f"Detected {target_class}")

    counter += 1

turret.stop()
camera.stop()
controller.stop()



#76,100 auf 100cm
#auf breite 70°
#auf höhe 90°