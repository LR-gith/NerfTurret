import time
import cv2
import requests
import io

SERVER_URL = 'http://192.168.188.112:5555'

def update_value_on_server(frame, values):
    success, encoded_image = cv2.imencode('.jpg', frame)
    if not success:
        print("Could not encode image")
        return False
    image_bytes = io.BytesIO(encoded_image.tobytes())
    image = {'image': ('frame.jpg', image_bytes, 'image/jpeg')}
    try:
        response = requests.post(f"{SERVER_URL}/update", data=values, files=image)
    except requests.exceptions.ConnectionError:
        print(f"Can't connect to server {SERVER_URL}")
        return False

    responseJson = response.json()
    print(f"confidence:, {responseJson["confidence"]}, x: {responseJson["x"]}, y: {responseJson["y"]}, x_angle: {responseJson["x_angle"]}, y_angle: {responseJson["y_angle"]},")
    return True

def get_value_from_server():
    try:
        response = requests.get(f"{SERVER_URL}/value")
    except requests.exceptions.ConnectionError:
        print(f"Can't connect to server {SERVER_URL}")
        return False

    responseJson = response.json()
    print(f"Current value: {responseJson["current_value"]}")
    return True

def log_to_server(message):
    try:
        response = requests.post(f"{SERVER_URL}/log", json={"message": message})
    except requests.exceptions.ConnectionError:
        print(f"Can't connect to server {SERVER_URL}")
        return False

    responseJson = response.json()
    print("Logged to Server:", responseJson["message"])
    return True

if __name__ == '__main__':
    i = 0
    connected = True
    while connected:
        print(f"Sending data {i} ...")
        connected = update_value_on_server(f"Seconds: {i}", None) and get_value_from_server()
        i+=1
        time.sleep(2)
