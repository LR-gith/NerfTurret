import cv2
from ultralytics import YOLO
import numpy as np

class Turret:

    def __init__(self, controller, camera, target_class, camera_size=(640, 480), camera_bandwidth=(90, 70), show_img=False):
        self.controller = controller
        self.camera = camera
        self.targetClass = target_class
        self.camera_width = camera_size[0]
        self.camera_height = camera_size[1]
        self.camera_width_angle = camera_bandwidth[0]
        self.camera_height_angle = camera_bandwidth[1]
        self.showImg = show_img
        self.__model = YOLO("yoloWeights/yolov5su.pt")
        self.counter = 0


    def run(self):
        x = None
        y = None
        x_angle = None
        y_angle = None

        ret, frame = self.camera.read()

        if not ret:
            print("Failed to grab frame!")
            return -1, 0, 0

        results = self.__model(frame, verbose=False)[0]
        highestConf = -1
        highestConfBox = None
        for box in results.boxes:
            cls_id = int(box.cls[0])
            label = self.__model.names[cls_id]

            if label.lower() == self.targetClass.lower():
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
            self.controller.align(x_angle, y_angle)
            cv2.circle(frame, (x,y),radius=1,color=(0, 0, 255),thickness=2)
        else:
            self.controller.defaultServoPosition()

        if self.showImg:
            cv2.imshow("Detection", frame)
            cv2.waitKey(1)
        values = {"conf": np.round(highestConf, 3), "x":x, "y":y, "relative_x_angle":x_angle, "relative_y_angle":y_angle, "absolut_x_angle":self.controller.getXServoAngle(), "absolut_y_angle":self.controller.getYServoAngle()}
        return frame, values


    def stop(self):
        if not self.showImg:
            cv2.destroyAllWindows()
        print("Stopping the Turret...")
