import io
import os
import time
from json import JSONDecodeError

import cv2
import requests
from dotenv import load_dotenv

from src.exception.exception import EncodeImageException
from src.exception.exception import ReconnectionFailedException

env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(env_path)
SERVER_IP = os.getenv('SERVER_IP')
PORT = os.getenv('PORT')
SERVER_URL = f'http://{SERVER_IP}:{PORT}'
FRAME_DOT_JPG_STRING = 'frame.jpg'
IMAGE_SLASH_JPEG_STRING = 'image/jpeg'

current_iteration = 0
print_iteration = 1


def initialize_connection():
    attempts = 0
    max_attempts = 10
    while attempts < max_attempts:
        if ping():
            break
        if attempts == 0: print(f"Can't connect to server {SERVER_URL}")
        print("Failed to connect, retrying in one second...")
        time.sleep(1)
        attempts += 1
    else:
        print("Failed to connect after multiple attempts.")
        return False
    return True


def reconnect():
    attempts = 0
    max_attempts = 5
    print(f"Can't connect to server {SERVER_URL}")
    while attempts < max_attempts:
        if ping():
            break
        print("Failed to connect, retrying in one second...")
        time.sleep(1)
        attempts += 1
    else:
        raise ReconnectionFailedException(
            "Failed to reconnect after multiple attempts.")
    return True


def print_detection_response_helper(response):
    global current_iteration
    response_json = response.json()
    if current_iteration % print_iteration == 0:
        print(', '.join(
            f"{key}: {value}" for key, value in response_json.items()))
    current_iteration += 1


def update_object_detection(frame, values):
    response = None
    success, encoded_image = cv2.imencode('.jpg', frame)
    if not success:
        raise EncodeImageException()
    image_bytes = io.BytesIO(encoded_image.tobytes())
    image = {
        'image': (FRAME_DOT_JPG_STRING, image_bytes, IMAGE_SLASH_JPEG_STRING)}
    try:
        response = requests.post(f"{SERVER_URL}/updateObjectDetection",
                                 data=values, files=image)
    except requests.exceptions.ConnectionError:
        if reconnect():
            renewed_image = {'image': (FRAME_DOT_JPG_STRING,
                                       create_new_buffer(image['image'][1]),
                                       IMAGE_SLASH_JPEG_STRING)}
            response = requests.post(f"{SERVER_URL}/updateObjectDetection",
                                     data=values, files=renewed_image)

    print_detection_response_helper(response)

    return True


def update_color_detection(frame, mask, values):
    response = None
    image_success, encoded_image = cv2.imencode('.jpg', frame)
    mask_success, encoded_mask = cv2.imencode('.jpg', mask)

    if image_success ^ mask_success:
        raise EncodeImageException()
    image_bytes = io.BytesIO(encoded_image.tobytes())
    mask_bytes = io.BytesIO(encoded_mask.tobytes())
    images = {
        'image': (FRAME_DOT_JPG_STRING, image_bytes, IMAGE_SLASH_JPEG_STRING),
        'mask': ('mask.jpg', mask_bytes, IMAGE_SLASH_JPEG_STRING)}

    try:
        response = requests.post(f"{SERVER_URL}/updateColorDetection",
                                 data=values, files=images)
    except requests.exceptions.ConnectionError:
        if reconnect():
            renewed_image = {'image': (FRAME_DOT_JPG_STRING,
                                       create_new_buffer(images['image'][1]),
                                       IMAGE_SLASH_JPEG_STRING),
                             'mask': ('mask.jpg',
                                      create_new_buffer(images['mask'][1]),
                                      IMAGE_SLASH_JPEG_STRING)
                             }
            response = requests.post(f"{SERVER_URL}/updateColorDetection",
                                     data=values, files=renewed_image)

    print_detection_response_helper(response)

    return True


def calculate_detection(data, image):
    global current_iteration
    response = None
    try:
        response = requests.post(f"{SERVER_URL}/calculateDetection", data=data,
                                 files=image)
    except requests.exceptions.ConnectionError:
        if reconnect():
            renewed_image = {'image': (image['image'][0],
                                       create_new_buffer(image['image'][1]),
                                       image['image'][2])}
            response = requests.post(f"{SERVER_URL}/calculateDetection",
                                     data=data, files=renewed_image)

    if response.status_code != 200:
        raise SystemError("server responded with an error code")
    try:
        response_json = response.json()
    except JSONDecodeError:
        raise ValueError("response isn't a json format")

    values = response_json['values']
    if current_iteration % print_iteration == 0:
        print(', '.join(f"{key}: {value}" for key, value in values.items()))
    current_iteration += 1
    return values


def create_new_buffer(old_buffer):
    return io.BytesIO(old_buffer.getvalue())


def get_value_from_server():
    try:
        response = requests.get(f"{SERVER_URL}/value")
    except requests.exceptions.ConnectionError:
        if reconnect():
            response = requests.get(f"{SERVER_URL}/value")

    response_json = response.json()
    print(f"Current value: {response_json["current_value"]}")
    return True


def update_only_image(frame):
    success, encoded_image = cv2.imencode('.jpg', frame)
    if not success:
        raise EncodeImageException()
    image_bytes = io.BytesIO(encoded_image.tobytes())
    image = {
        'image': (FRAME_DOT_JPG_STRING, image_bytes, IMAGE_SLASH_JPEG_STRING)}
    try:
        requests.post(f"{SERVER_URL}/updateOnlyImage", files=image)
    except requests.exceptions.ConnectionError:
        if reconnect():
            renewed_image = {'image': (FRAME_DOT_JPG_STRING,
                                       create_new_buffer(image['image'][1]),
                                       IMAGE_SLASH_JPEG_STRING)}
            requests.post(f"{SERVER_URL}/updateOnlyImage", files=renewed_image)

    return True


def get_color_selections():
    try:
        response = requests.get(f"{SERVER_URL}/get_color_selection_list")
    except requests.exceptions.ConnectionError:
        if reconnect():
            response = requests.get(f"{SERVER_URL}/get_color_selection_list")

    response_json = response.json()
    if response_json["status"] == "ok":
        return True, response_json["colors"]
    else:
        return False, None


def clear_color_selections():
    try:
        response = requests.get(f"{SERVER_URL}/clear_color_selection")
    except requests.exceptions.ConnectionError:
        if reconnect():
            response = requests.get(f"{SERVER_URL}/clear_color_selection")

    response_json = response.json()
    if not response_json["status"] and not response_json["colors"]:
        return True
    else:
        return False


def redirect_to_color_selection():
    try:
        response = requests.get(f"{SERVER_URL}/redirectToColorSelection")
    except requests.exceptions.ConnectionError:
        if reconnect():
            response = requests.get(f"{SERVER_URL}/redirectToColorSelection")

    response_json = response.json()
    if response_json["status"] == "redirected":
        return True
    else:
        return False


def log_to_server(message):
    try:
        requests.post(f"{SERVER_URL}/log", json={"message": message})
    except requests.exceptions.ConnectionError:
        if reconnect():
            requests.post(f"{SERVER_URL}/log", json={"message": message})

    return True


def ping():
    try:
        response = requests.get(f"{SERVER_URL}/ping", timeout=2)
    except (requests.exceptions.ConnectionError,
            requests.exceptions.ReadTimeout, TimeoutError):
        return False

    return response.content.decode() == "pong"


def set_print_iteration(iteration):
    global print_iteration
    print_iteration = iteration


if __name__ == '__main__':
    raise NotImplementedError("Not supported to run Client as main")
