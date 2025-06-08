import cv2
import threading
import time

class CameraThread:
    def __init__(self, camera_index=0):
        self.cap = cv2.VideoCapture(camera_index)
        self.ret, self.frame = self.cap.read()
        if not self.cap.isOpened():
            print("Error: Could not open webcam.")
            exit()
        self.lock = threading.Lock()
        self.running = True

        self.thread = threading.Thread(target=self.update, daemon=True)
        self.thread.start()

    def update(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.ret = ret
                    self.frame = frame
            time.sleep(0.01)  # small delay to avoid CPU hogging

    def read(self):
        with self.lock:
            return self.ret, self.frame.copy()

    def stop(self):
        self.running = False
        self.thread.join()
        self.cap.release()
