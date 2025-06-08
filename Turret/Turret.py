import sys
import os
import cv2
import numpy as np
from ultralytics import YOLO
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PiController.PiController import PiController

width = 640
height = 480
widthAng = 90
heightAng = 70

if len(sys.argv) > 1:
    target_class = sys.argv[1]
else:
    target_class = 'person'

controller = PiController(18,19,2,3)

# Load YOLOv5 model (automatically downloads if not available)
model = YOLO("yolov5su.pt")


# Start video capture from webcam
cap = cv2.VideoCapture(0)  # 0 = default camera


if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

counter = 0
while True:
    ret, frame = cap.read()

    if not ret:
        print("Failed to grab frame.")
        break

    # Run object detection
    results = model(frame,verbose=False)[0]
    highestConf = -1
    highestConfBox = None
    for box in results.boxes:
        cls_id = int(box.cls[0])
        label = model.names[cls_id]

        if label.lower() == target_class.lower():
            conf = float(box.conf[0])
            if conf > highestConf:
                highestConf = conf
                highestConfBox = box

    if highestConfBox is not None:
        x1, y1, x2, y2 = map(int, highestConfBox.xyxy[0])
        x = (x1+x2)//2
        y = (y1+y2)//2
        xAngle = int((widthAng / width) * (x - width/2))
        yAngle = int(-(heightAng / height) * (y - height/2))
        controller.align(xAngle, yAngle)
        if counter % 1 == 0:
            print("x:   " ,xAngle, "    y:  " ,yAngle)
        #controller.align()
        #cv2.circle(frame, (x,y),radius=1,color=(0, 0, 255),thickness=2)

    if counter % 1 == 0:
        if highestConf == -1:
            print("Detected no", target_class)
        else:
            print("Detected", target_class, " With confidence:", np.round(highestConf, 3))

    counter +=1
    #cv2.imshow("Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()

#76,100 auf 100cm
#auf breite 70°
#auf höhe 90°