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

global running
global counter
global args
global camera
global controller
global detector


def main():
    global running, counter, args, camera, controller, detector
    running = True
    counter = 0

    args = initialize_args()
    validate_args()

    exit_thread = threading.Thread(target=wait_for_exit, daemon=True)
    exit_thread.start()

    initialize_camera_and_controller()
    conditional_color_selector()
    initialize_detector()

    running_loop()

    stop()


def initialize_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--iteration", type=int,
                        help="output after I iterations", default=5,
                        dest="print_iteration")
    parser.add_argument("-c", "--class", type=str,
                        help="detects this object class C", default="person",
                        dest="target_class")
    parser.add_argument("-cr", "--color_range", type=int,
                        help="range above and below detected color", default=40)
    parser.add_argument("-img", "--showImg", action="store_true",
                        help="When used an window will display the camera after detection",
                        dest="show_img")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Gives extra terminal output")
    parser.add_argument("-p", "--pickColor", action="store_true",
                        help="When used lets you pick colors yourself",
                        dest="selector_running")
    parser.add_argument("-rw", "--runWebsite", action="store_true",
                        help="When set to false the website isn't used",
                        dest="website_running")
    return parser.parse_args()


def validate_args():
    if args.website_running and args.show_img:
        args.showImg = False
        print("Wont display image because its already displayed on the website")
    if not args.website_running and args.selector_running:
        print("Color selector can't run because not running on website")
        args.target_class = "#ffffff"

    # initializes connection to the server
    if args.website_running and not client.initialize_connection():
        exit("Failed to connect to server")

    print("iteration: ", args.print_iteration, ", class: ", args.target_class,
          ", color_range: ", args.color_range, ", show image: ", args.show_img,
          ", verbose: ",
          args.verbose, ", pickColor: ", args.selector_running,
          ", runWebsite: ",
          args.website_running)


def wait_for_exit():
    global running
    input("Press [Enter] to exit...\n")
    running = False


def initialize_camera_and_controller():
    global camera, controller
    from src.turret.camera import Camera
    from src.turret.pi_controller import PiController, running_on_pi

    if not running_on_pi and args.website_running:
        client.log_to_server("Turret isn't operating on pi!")
        client.log_to_server("No GPIO output will be done!")
    elif not running_on_pi and not args.website_running:
        print("Turret isn't operating on pi!")
        print("No GPIO output will be done!")

    controller = PiController(verbose=args.verbose)
    controller.default_servo_position()
    camera = Camera()


def conditional_color_selector():
    global running
    if args.website_running:
        client.clear_color_selections()
        client.set_print_iteration(args.print_iteration)
        if args.selector_running:
            client.redirect_to_color_selection()

        while args.selector_running:
            ret, frame = camera.read()
            if not ret:
                print("Failed to grab frame!")
                break

            if not client.update_only_image(frame):
                print("Failed to update image")
                running = False

            valid, colors = client.get_color_selections()

            if valid:
                args.selector_running = False
                print(colors)
                args.target_class = colors
            else:
                time.sleep(0.5)


def initialize_detector():
    global running, detector

    from src.detection import object_detection
    from src.detection import color_detection

    if object_detection.is_class(args.target_class):
        detector = object_detection.ObjectDetection(
            target_class=args.target_class,
            website_running=args.website_running,
            show_img=args.show_img
        )
    else:
        detector = color_detection.ColorDetection(
            target_class=args.target_class,
            color_range=args.color_range,
            website_running=args.website_running,
            show_img=args.show_img
        )

    print(f"Target class: {detector.target_class}")


def running_loop():
    global running, counter
    while running:
        ret, frame = camera.read()
        if not ret:
            print("Failed to grab frame!")
            break

        if args.website_running:
            try:
                with_website(frame)
            except ReconnectionFailedException as e:
                print(str(e))
                running = False
        else:
            without_website(frame)

        counter += 1


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

    data = {"website_running": args.website_running,
            "detector_class": detector.__class__.__name__,
            "detector_target_class": target_class_copy,
            "detector_color_range": detector.color_range,
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

    if counter % args.print_iteration == 0:
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
    if counter % args.print_iteration == 0:
        if confidence == -1:
            print(f"No {args.target_class} object detected")
        else:
            print(f"Detected {args.target_class} object")


def stop():
    detector.stop()
    camera.stop()
    controller.stop()


if __name__ == '__main__':
    main()
