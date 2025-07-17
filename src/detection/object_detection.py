import os

import cv2
import numpy as np
from dotenv import load_dotenv
from ultralytics import YOLO

file_path = os.path.dirname(__file__)
weight_path = os.path.join(file_path, "..", "..", "resources", "yolo_weights",
                           "yolov5su.pt")

env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(env_path)


def is_class(detection_class):
    return detection_class in classes


class ObjectDetection:

    def __init__(self, target_class, website_running, show_img=False):
        self.target_class = target_class
        self.camera_width = int(os.getenv('CAMERA_WIDTH'))
        self.camera_height = int(os.getenv('CAMERA_HEIGHT'))
        self.camera_width_angle = int(os.getenv('CAMERA_BANDWIDTH_WIDTH_ANGLE'))
        self.camera_height_angle = int(
            os.getenv('CAMERA_BANDWIDTH_HEIGHT_ANGLE'))
        self.color_range = 0  # only set to use one variable for a color and object detection object
        self.website_running = website_running
        self.show_img = show_img
        self.__model = YOLO(weight_path)


    def detect(self, frame):
        x = None
        y = None
        x_angle = 0
        y_angle = 0

        results = self.__model(frame, verbose=False)[0]
        highest_conf = -1
        highest_conf_box = None
        for box in results.boxes:
            cls_id = int(box.cls[0])
            label = self.__model.names[cls_id]

            if label.lower() == self.target_class.lower():
                conf = float(box.conf[0])
                if conf > highest_conf:
                    highest_conf = conf
                    highest_conf_box = box

        if highest_conf_box is not None:
            x1, y1, x2, y2 = map(int, highest_conf_box.xyxy[0])
            x = (x1 + x2) // 2
            y = (y1 + y2) // 2
            x_angle = int((self.camera_width_angle / self.camera_width) * (
                    x - self.camera_width / 2))
            y_angle = int(-(self.camera_height_angle / self.camera_height) * (
                    y - self.camera_height / 2))
            cv2.circle(frame, (x, y), radius=1, color=(0, 0, 255), thickness=2)

        if self.show_img and not self.website_running:
            cv2.imshow("Object detection", frame)
            cv2.waitKey(1)

        values = {"conf": float(np.round(highest_conf, 3)), "x": x, "y": y,
                  "relative_x_angle": x_angle,
                  "relative_y_angle": y_angle, "absolut_x_angle": "None",
                  "absolut_y_angle": "None"}
        return frame, None, values


    def stop(self):
        if self.show_img:
            cv2.destroyAllWindows()
        print("Stopping the object detection")


classes = [
    "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train",
    "truck", "boat",
    "traffic light", "fire hydrant", "stop sign", "parking meter", "bench",
    "bird", "cat", "dog",
    "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack",
    "umbrella",
    "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball",
    "kite",
    "baseball bat", "baseball glove", "skateboard", "surfboard",
    "tennis racket", "bottle",
    "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple",
    "sandwich",
    "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake",
    "chair", "couch",
    "potted plant", "bed", "dining table", "toilet", "tv", "laptop", "mouse",
    "remote",
    "keyboard", "cell phone", "microwave", "oven", "toaster", "sink",
    "refrigerator", "book",
    "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush"
]
