import io
import os
import sys
import threading
import argparse
import time

import cv2
import webcolors

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import Client

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--iteration", type=int, help="output after I iterations", default=5)
parser.add_argument("-c", "--class", type=str, help="detects this object class C", default="person", dest="targetClass")
parser.add_argument("-cr", "--color_range", type=int, help="range above and below detected color", default=40)
parser.add_argument("-img", "--showImg", action="store_true", help="When used an window will display the camera after detection")
parser.add_argument("-v", "--verbose", action="store_true", help="Gives extra terminal output")
parser.add_argument("-p", "--pickColor", action="store_true", help="When used lets you pick colors yourself")
parser.add_argument("-rw", "--runWebsite", action="store_true", help="When set to false the website isn't used")
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
from PiController import PiController, running_on_pi
from Detection import ObjectDetection
from Detection import ColorDetection

if not running_on_pi and website_running:
    Client.log_to_server("Turret isn't operating on pi!")
    Client.log_to_server("No GPIO output will be done!")
elif not running_on_pi and not website_running:
    print("Turret isn't operating on pi!")
    print("No GPIO output will be done!")


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

print("iteration: ",print_iteration , ", class: ", target_class, ", color_range: ", color_range, ", show image: ", show_img, ", verbose: ", verbose, ", pickColor: ", selector_running, ", runWebsite: ", website_running)


controller = PiController(X_SERVO_PIN, Y_SERVO_PIN, CHARGE_PIN, SHOOT_PIN, verbose=verbose)

camera = Camera(0)


exit_thread = threading.Thread(target=wait_for_exit, daemon=True)
exit_thread.start()


if website_running:
    Client.clearColorSelections()
    Client.setPrintIteration(print_iteration)
    if selector_running:
        Client.redirectToColorSelection()


    while selector_running:
        ret, frame = camera.read()
        if not ret:
            print("Failed to grab frame!")
            break

        if not Client.updateOnlyImage(frame):
            print("Failed to update image")
            running = False

        valid, colors = Client.getColorSelections()

        if valid:
            selector_running = False
            print(colors)
            target_class = colors
        else:
            time.sleep(0.5)

if ObjectDetection.isClass(target_class):
    detector = ObjectDetection.ObjectDetection(target_class=target_class, show_img=show_img)
else:
    detector = ColorDetection.ColorDetection(target_class=target_class, color_range=color_range, show_img=show_img)

print(detector.target_class)


def with_website(camera_frame):

    success, encoded_image = cv2.imencode('.jpg', camera_frame)
    if not success:
        print("Could not encode image")
        return False
    image_bytes = io.BytesIO(encoded_image.tobytes())
    image = {'image': ('frame.jpg', image_bytes, 'image/jpeg')}
    target_class_copy = detector.target_class
    if detector.__class__.__name__ == "ColorDetection":
        try:
            target_class_copy = webcolors.rgb_to_hex(detector.target_class)
        except ValueError:
            print("Isn't a color")

    data = {"detector_class" : detector.__class__.__name__,
            "detector_target_class" : target_class_copy,
            "detector_color_range" : detector.color_range,
            "detector_camera_width" : detector.camera_width,
            "detector_camera_height" : detector.camera_height,
            "detector_camera_width_angle" : detector.camera_width_angle,
            "detector_camera_height_angle" : detector.camera_height_angle,
            "detector_showImg" : detector.showImg,
            "absolut_x_angle" : controller.getXServoAngle(),
            "absolut_y_angle" : controller.getYServoAngle()}

    detection_frame, mask, values = Client.calculate_detection(data, image)

    x_Angle = values['relative_x_angle']
    y_Angle = values['relative_y_angle']
    absolut_x_angle = values['absolut_x_angle']
    absolut_y_angle = values['absolut_y_angle']

    controller.align(x_Angle, y_Angle)
    if absolut_x_angle != controller.xServoAngle or absolut_y_angle != controller.yServoAngle:
        raise Exception("Absolut angles from Server and Turret are not synchronized")

    confidence = values["conf"]
    if mask is not None and mask.size > 0:
        Client.update_color_detection(detection_frame, mask, values)
    else:
        Client.update_object_detection(detection_frame, values)

    if counter % print_iteration == 0:
        if confidence == -1:
            Client.log_to_server(f"No {target_class_copy} object detected")
        else:
            Client.log_to_server(f"Detected {target_class_copy} object")


def without_website(camera_frame):
    frame, mask, values = detector.detect(camera_frame)
    confidence = values["conf"]
    x_Angle = values['relative_x_angle']
    y_Angle = values['relative_y_angle']
    controller.align(x_Angle, y_Angle)
    values['absolut_x_angle'] = controller.getXServoAngle()
    values['absolut_y_angle'] = controller.getYServoAngle()
    if counter % print_iteration == 0:
        if confidence == -1:
            print(f"No {target_class} object detected")
        else:
            print(f"Detected {target_class} object")

while running:
    ret, frame = camera.read()
    if not ret:
        print("Failed to grab frame!")
        break

    if website_running:
        with_website(frame)
    else:
        without_website(frame)

    counter += 1


detector.stop()
camera.stop()
controller.stop()


#76,100 auf 100cm
#auf breite 70°
#auf höhe 90°