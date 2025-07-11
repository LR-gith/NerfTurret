import cv2
import numpy as np
import webcolors
from webcolors import IntegerRGB


class ColorDetection:

    def __init__(self, target_class, color_range, website_running,
                 camera_size=(640, 480), camera_bandwidth=(90, 70),
                 show_img=False):
        try:
            self.target_class = webcolors.name_to_rgb(target_class)
        except (ValueError, AttributeError):
            self.target_class = self.color_mean(target_class)

        if color_range not in range(0, 255):
            raise AttributeError("Invalid color range")

        self.color_range = color_range
        self.lower_rgb, self.upper_rgb = self.set_rgb_bounds(self.target_class)
        self.camera_size = camera_size
        self.camera_width = camera_size[0]
        self.camera_height = camera_size[1]
        self.camera_bandwidth = camera_bandwidth
        self.camera_width_angle = camera_bandwidth[0]
        self.camera_height_angle = camera_bandwidth[1]
        self.website_running = website_running
        self.show_img = show_img
        self.counter = 0


    def detect(self, frame):
        x_mid = None
        y_mid = None
        x_angle = 0
        y_angle = 0
        conf = -1

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mask = cv2.inRange(rgb, self.lower_rgb, self.upper_rgb)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                       cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)
            if area > 100:
                conf = 1
                x, y, w, h = cv2.boundingRect(largest_contour)
                x_mid = x + (w // 2)
                y_mid = y + (h // 2)
                x_angle = int((self.camera_width_angle / self.camera_width) * (
                        x_mid - self.camera_width / 2))
                y_angle = int(
                    -(self.camera_height_angle / self.camera_height) * (
                            y_mid - self.camera_height / 2))
                cv2.circle(frame, (x_mid, y_mid), radius=1, color=(0, 0, 255),
                           thickness=2)

        if self.show_img and not self.website_running:
            cv2.imshow("Mask", mask)
            cv2.imshow("detection", frame)
            cv2.waitKey(1)

        values = {"conf": conf, "x": x_mid, "y": y_mid,
                  "relative_x_angle": x_angle,
                  "relative_y_angle": y_angle, "absolut_x_angle": "None",
                  "absolut_y_angle": "None"}
        return frame, mask, values


    def set_rgb_bounds(self, rgb_color):
        if (isinstance(rgb_color, tuple) and len(rgb_color) == 3) or isinstance(
                rgb_color, IntegerRGB):
            rgb_color = np.array(rgb_color)

            lower_rgb = np.clip(rgb_color - self.color_range, 0, 255)
            upper_rgb = np.clip(rgb_color + self.color_range, 0, 255)
        else:
            raise ValueError("Type must be tuple or IntegerRGB")

        return lower_rgb, upper_rgb


    def color_mean(self, hex_colors) -> tuple[int, int, int]:
        if isinstance(hex_colors, str):
            hex_colors = [hex_colors]
        if type(hex_colors) is not list:
            raise ValueError("Type must be an array!")
        rgb_red = 0
        rgb_green = 0
        rgb_blue = 0
        for color in hex_colors:
            rgb_color = webcolors.hex_to_rgb(str(color))
            rgb_red += rgb_color[0]
            rgb_green += rgb_color[1]
            rgb_blue += rgb_color[2]
        size = len(hex_colors)
        rgb_red = rgb_red // size
        rgb_green = rgb_green // size
        rgb_blue = rgb_blue // size
        return rgb_red, rgb_green, rgb_blue


    def stop(self):
        if self.show_img:
            cv2.destroyAllWindows()
        print("Stopping the color detection")
