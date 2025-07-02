import os
import time
import cv2
import requests
import io
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(env_path)
SERVER_IP=os.getenv('SERVER_IP')
PORT=os.getenv('PORT')
SERVER_URL = f'http://{SERVER_IP}:{PORT}'

current_iteration = 0
print_iteration = 1

def initializeConnection():
    attempts = 0
    max_attempts = 10
    while attempts < max_attempts :
        if ping():
            return True
        if attempts == 0: print(f"Can't connect to server {SERVER_URL}")
        print("Failed to connect, retrying in one second...")
        time.sleep(1)
        attempts += 1
    else:
        print("Failed to connect after multiple attempts.")
        return False

def reconnect():
    attempts = 0
    max_attempts = 5
    print(f"Can't connect to server {SERVER_URL}")
    while attempts < max_attempts:
        if ping():
            return True
        print("Failed to connect, retrying in one second...")
        time.sleep(1)
        attempts += 1
    else:
        exit("Failed to reconnect after multiple attempts.")

def update_color_detection(frame, mask, values):
    global current_iteration
    image_success, encoded_image = cv2.imencode('.jpg', frame)
    mask_success, encoded_mask = cv2.imencode('.jpg', mask)

    if image_success ^ mask_success:
        print("Could not encode image")
        return False
    image_bytes = io.BytesIO(encoded_image.tobytes())
    mask_bytes = io.BytesIO(encoded_mask.tobytes())
    images = {'image': ('frame.jpg', image_bytes, 'image/jpeg'),'mask': ('mask.jpg', mask_bytes, 'image/jpeg')}

    try:
        response = requests.post(f"{SERVER_URL}/updateColorDetection", data=values, files=images)
    except requests.exceptions.ConnectionError:
        return reconnect()


    responseJson = response.json()
    if current_iteration % print_iteration == 0:
        print(f"confidence:, {responseJson["confidence"]}, "
              f"x: {responseJson["x"]}, y: {responseJson["y"]}, "
              f"relative_x_angle: {responseJson["relative_x_angle"]}, "
              f"relative_y_angle: {responseJson["relative_y_angle"]},"
              f"absolut_x_angle: {responseJson["absolut_x_angle"]},"
              f"absolut_y_angle: {responseJson["absolut_y_angle"]},")
    current_iteration += 1
    return True

def update_object_detection(frame, values):
    global current_iteration
    success, encoded_image = cv2.imencode('.jpg', frame)
    if not success:
        print("Could not encode image")
        return False
    image_bytes = io.BytesIO(encoded_image.tobytes())
    image = {'image': ('frame.jpg', image_bytes, 'image/jpeg')}
    try:
        response = requests.post(f"{SERVER_URL}/updateObjectDetection", data=values, files=image)
    except requests.exceptions.ConnectionError:
        return reconnect()


    responseJson = response.json()
    if current_iteration % print_iteration == 0:
        print(f"confidence:, {responseJson["confidence"]}, "
              f"x: {responseJson["x"]}, y: {responseJson["y"]}, "
              f"relative_x_angle: {responseJson["relative_x_angle"]}, "
              f"relative_y_angle: {responseJson["relative_y_angle"]},"
              f"absolut_x_angle: {responseJson["absolut_x_angle"]},"
              f"absolut_y_angle: {responseJson["absolut_y_angle"]},")
    current_iteration += 1
    return True

def get_value_from_server():
    try:
        response = requests.get(f"{SERVER_URL}/value")
    except requests.exceptions.ConnectionError:
        return reconnect()

    responseJson = response.json()
    print(f"Current value: {responseJson["current_value"]}")
    return True

def log_to_server(message):
    try:
        requests.post(f"{SERVER_URL}/log", json={"message": message})
    except requests.exceptions.ConnectionError:
        print(f"Can't connect to server {SERVER_URL}")
        return reconnect()

    return True

def ping():
    try:
        response = requests.get(f"{SERVER_URL}/ping")
    except requests.exceptions.ConnectionError:
        return False

    if response.content.decode() == "pong":
        return True
    else:
        return False

def setPrintIteration(iteration):
    global print_iteration
    print_iteration = iteration


if __name__ == '__main__':
    raise NotImplementedError("Not supported to run Client as main")
