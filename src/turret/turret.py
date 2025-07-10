import argparse
import io
import os
import sys
import threading
import time

import cv2
import webcolors

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.turret import client
from src.exception.exception import EncodeImageException
from src.exception.exception import AngleMissmatchException
from src.exception.exception import ReconnectionFailedException

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--iteration", type=int,
                    help="output after I iterations", default=5)
parser.add_argument("-c", "--class", type=str,
                    help="detects this object class C", default="person",
                    dest="targetClass")
parser.add_argument("-cr", "--color_range", type=int,
                    help="range above and below detected color", default=40)
parser.add_argument("-img", "--showImg", action="store_true",
                    help="When used an window will display the camera after detection")
parser.add_argument("-v", "--verbose", action="store_true",
                    help="Gives extra terminal output")
parser.add_argument("-p", "--pickColor", action="store_true",
                    help="When used lets you pick colors yourself")
parser.add_argument("-rw", "--runWebsite", action="store_true",
                    help="When set to false the website isn't used")
args = parser.parse_args()

print_iteration = args.iteration
target_class = args.targetClass
color_range = args.color_range
show_img = args.showImg
verbose = args.verbose
selector_running = args.pickColor
website_running = args.runWebsite

if website_running and show_img:
    show_img = False
    print("Wont display image because its already displayed on the website")
if not website_running and selector_running:
    print("Color selector can't run because not running on website")
    target_class = "#ffffff"

# initializes connection to the server
if website_running and not client.initialize_connection():
    exit("Failed to connect to server")

from camera import Camera
from pi_controller import PiController, running_on_pi
from src.detection import object_detection
from src.detection import color_detection

if not running_on_pi and website_running:
    client.log_to_server("Turret isn't operating on pi!")
    client.log_to_server("No GPIO output will be done!")
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


exit_thread = threading.Thread(target=wait_for_exit, daemon=True)
exit_thread.start()

print("iteration: ", print_iteration, ", class: ", target_class,
      ", color_range: ", color_range, ", show image: ", show_img, ", verbose: ",
      verbose, ", pickColor: ", selector_running, ", runWebsite: ",
      website_running)

controller = PiController(X_SERVO_PIN, Y_SERVO_PIN, CHARGE_PIN, SHOOT_PIN,
                          verbose=verbose)
camera = Camera(0)

if website_running:
    client.clear_color_selections()
    client.set_print_iteration(print_iteration)
    if selector_running:
        client.redirect_to_color_selection()

    while selector_running:
        ret, frame = camera.read()
        if not ret:
            print("Failed to grab frame!")
            break

        if not client.update_only_image(frame):
            print("Failed to update image")
            running = False

        valid, colors = client.get_color_selections()

        if valid:
            selector_running = False
            print(colors)
            target_class = colors
        else:
            time.sleep(0.5)

if object_detection.is_class(target_class):
    detector = object_detection.ObjectDetection(target_class=target_class,
                                                website_running=website_running,
                                                show_img=show_img
                                                )
else:
    detector = color_detection.ColorDetection(target_class=target_class,
                                              color_range=color_range,
                                              website_running=website_running,
                                              show_img=show_img
                                              )

print(f"Target class: {detector.target_class}")


def with_website(camera_frame):
    success, encoded_image = cv2.imencode('.jpg', camera_frame)
    if not success:
        raise EncodeImageException()

    image_bytes = io.BytesIO(encoded_image.tobytes())
    image = {'image': ('frame.jpg', image_bytes, 'image/jpeg')}
    target_class_copy = detector.target_class
    if detector.__class__.__name__ == "ColorDetection":
        try:
            target_class_copy = webcolors.rgb_to_hex(detector.target_class)
        except ValueError:
            print("Isn't a color")

    data = {"website_running": website_running,
            "detector_class": detector.__class__.__name__,
            "detector_target_class": target_class_copy,
            "detector_color_range": detector.color_range,
            "detector_camera_width": detector.camera_width,
            "detector_camera_height": detector.camera_height,
            "detector_camera_width_angle": detector.camera_width_angle,
            "detector_camera_height_angle": detector.camera_height_angle,
            "detector_show_img": detector.show_img,
            "absolut_x_angle": controller.get_x_servo_angle(),
            "absolut_y_angle": controller.get_y_servo_angle()}

    values = client.calculate_detection(data, image)

    x_angle = values['relative_x_angle']
    y_angle = values['relative_y_angle']
    absolut_x_angle = values['absolut_x_angle']
    absolut_y_angle = values['absolut_y_angle']

    controller.align(x_angle, y_angle)
    if absolut_x_angle != controller.x_servo_angle or absolut_y_angle != controller.y_servo_angle:
        raise AngleMissmatchException(
            "Absolut angles from server and turret are not synchronized")

    confidence = values["conf"]

    if counter % print_iteration == 0:
        if confidence == -1:
            client.log_to_server(f"No {target_class_copy} object detected")
        else:
            client.log_to_server(f"Detected {target_class_copy} object")


def without_website(camera_frame):
    _, _, values = detector.detect(camera_frame)
    confidence = values["conf"]
    x_angle = values['relative_x_angle']
    y_angle = values['relative_y_angle']
    controller.align(x_angle, y_angle)
    values['absolut_x_angle'] = controller.get_x_servo_angle()
    values['absolut_y_angle'] = controller.get_y_servo_angle()
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
        try:
            with_website(frame)
        except ReconnectionFailedException as e:
            print(str(e))
            running = False
    else:
        without_website(frame)

    counter += 1

detector.stop()
camera.stop()
controller.stop()
