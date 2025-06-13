import cv2
from ultralytics import YOLO



class Turret:

    def __init__(self, controller, camera, target_class, camera_size=(640, 480), camera_bandwidth=(90, 70),running_on_pi=True):
        if running_on_pi: self.controller = controller
        self.camera = camera
        self.targetClass = target_class
        self.camera_width = camera_size[0]
        self.camera_height = camera_size[1]
        self.camera_width_angle = camera_bandwidth[0]
        self.camera_height_angle = camera_bandwidth[1]
        self.running_on_pi = running_on_pi
        self.__model = YOLO("yoloWeights/yolov5su.pt")
        self.counter = 0


    def run(self):
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
            if self.running_on_pi: self.controller.align(x_angle, y_angle)
            if not self.running_on_pi:
                cv2.circle(frame, (x,y),radius=1,color=(0, 0, 255),thickness=2)
        else:
            if self.running_on_pi: self.controller.defaultServoPosition()

        if not self.running_on_pi:
            cv2.imshow("Detection", frame)
            cv2.waitKey(1)

        return highestConf, x_angle, y_angle


    def stop(self):
        if not self.running_on_pi:
            cv2.destroyAllWindows()

        print("Stopping the Turret...")
