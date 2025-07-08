import os

import cv2
import numpy as np
from ultralytics import YOLO
weight_path = os.path.abspath(os.path.join("..", "yoloWeights", "yolov5su.pt"))



def isClass(detection_class):
    return detection_class in classes


class ObjectDetection:

    def __init__(self, target_class, camera_size=(640, 480), camera_bandwidth=(90, 70), show_img=False):
        self.target_class = target_class
        self.camera_width = camera_size[0]
        self.camera_height = camera_size[1]
        self.camera_width_angle = camera_bandwidth[0]
        self.camera_height_angle = camera_bandwidth[1]
        self.color_range = 0 #only set to use one variable for color and object detection object
        self.showImg = show_img
        self.__model = YOLO(weight_path)
        self.counter = 0

    def detect(self, frame):
        x = None
        y = None
        x_angle = 0
        y_angle = 0

        results = self.__model(frame, verbose=False)[0]
        highestConf = -1
        highestConfBox = None
        for box in results.boxes:
            cls_id = int(box.cls[0])
            label = self.__model.names[cls_id]

            if label.lower() == self.target_class.lower():
                conf = float(box.conf[0])
                if conf > highestConf:
                    highestConf = conf
                    highestConfBox = box

        if highestConfBox is not None:
            x1, y1, x2, y2 = map(int, highestConfBox.xyxy[0])
            x = (x1 + x2) // 2
            y = (y1 + y2) // 2
            x_angle = int((self.camera_width_angle / self.camera_width) * (x - self.camera_width / 2))
            y_angle = int(-(self.camera_height_angle / self.camera_height) * (y - self.camera_height / 2))
            cv2.circle(frame, (x, y), radius=1, color=(0, 0, 255), thickness=2)


        if self.showImg:
            cv2.imshow("Object detection", frame)
            cv2.waitKey(1)
        values = {"conf": np.round(highestConf, 3), "x": x, "y": y, "relative_x_angle": x_angle,
                  "relative_y_angle": y_angle, "absolut_x_angle": "None",
                  "absolut_y_angle": "None"}
        return frame, None, values

    def stop(self):
        if not self.showImg:
            cv2.destroyAllWindows()
        print("Stopping the object detection")


classes = [
    "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck", "boat",
    "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat", "dog",
    "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella",
    "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite",
    "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle",
    "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich",
    "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair", "couch",
    "potted plant", "bed", "dining table", "toilet", "tv", "laptop", "mouse", "remote",
    "keyboard", "cell phone", "microwave", "oven", "toaster", "sink", "refrigerator", "book",
    "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush"
]