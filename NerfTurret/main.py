import threading
import argparse
import time

import Client


parser = argparse.ArgumentParser()
parser.add_argument("-i", "--iteration", type=int, help="output after I iterations", default=5)
parser.add_argument("-c", "--class", type=str, help="detects this object class C", default="person", dest="targetClass")
parser.add_argument("-cr", "--color_range", type=int, help="range above and below detected color", default=40)
parser.add_argument("-img", "--showImg", action="store_true", help="When used an window will display the camera after detection")
parser.add_argument("-v", "--verbose", action="store_true", help="Gives extra terminal output")
parser.add_argument("-p", "--pickColor", action="store_true", help="When used lets you pick colors yourself")
parser.add_argument("-w","--runWebsite", action="store_true", help="When set to false the website isn't used")
args = parser.parse_args()

print_iteration = args.iteration
target_class = args.targetClass
color_range = args.color_range
show_img = args.showImg
verbose = args.verbose
selector_running = args.pickColor
website_running = args.runWebsite


# initializes connection to the server
if website_running:
    if not Client.initializeConnection():
        exit("Failed to connect to Server")

from Camera import Camera
from Turret import Turret
from PiController import PiController, running_on_pi

if not running_on_pi and not website_running:
    Client.log_to_server("Turret isn't operating on pi!")
    Client.log_to_server("No GPIO output will be done!")


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

print("iteration: ",print_iteration , ", class: ", target_class, ", color_range: ", color_range, "show image: ", show_img, ", verbose: ", verbose, " , pickColor: ", selector_running, " , runWebsite: ", website_running)


controller = PiController(X_SERVO_PIN, Y_SERVO_PIN, CHARGE_PIN, SHOOT_PIN, verbose=verbose)
camera = Camera(0)
turret = Turret(controller, camera, target_class, color_range, show_img=show_img)
if website_running: Client.setPrintIteration(print_iteration)

exit_thread = threading.Thread(target=wait_for_exit, daemon=True)
exit_thread.start()

if website_running:
    Client.clearColorSelections()
    if selector_running:
        Client.redirectToColorSelection()

while selector_running:
    ret, frame = camera.read()
    if website_running:
        if not Client.updateOnlyImage(frame):
            print("Failed to update image")
            running = False

    valid, colors = Client.getColorSelections()

    if valid:
        selector_running = False
        print(colors)
        target_class = turret.color_mean(colors)
        print(target_class)
        turret.setTargetClassToRGBValue(target_class,color_range)
    else:
        time.sleep(0.5)


while running:
    frame, mask, values = turret.run()
    confidence = values["conf"]
    if website_running:
        if mask is not None and mask.size > 0:
            Client.update_color_detection(frame, mask, values)
        else:
            Client.update_object_detection(frame, values)

        if counter % print_iteration == 0:
            if confidence == -1:
                Client.log_to_server(f"No {target_class} object detected")
            else:
                Client.log_to_server(f"Detected {target_class} object")
    else:
        if counter % print_iteration == 0:
            if confidence == -1:
                print(f"No {target_class} object detected")
            else:
                print(f"Detected {target_class} object")

    counter += 1

turret.stop()
camera.stop()
controller.stop()



#76,100 auf 100cm
#auf breite 70°
#auf höhe 90°