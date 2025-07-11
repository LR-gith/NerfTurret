import os

import cv2
import numpy as np

import src.detection.object_detection
from detection.object_detection import ObjectDetection


def test_is_class_true():
    return_value = src.detection.object_detection.is_class("person")
    assert return_value == True


def test_is_class_false():
    return_value = src.detection.object_detection.is_class("test")
    assert return_value == False


def test_init_valid(mocker):
    object_detect = ObjectDetection("fork", False)

    assert object_detect.target_class == "fork"
    assert object_detect.counter == 0


def test_detect_no_object():
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    no_object = ObjectDetection("person", 0)
    frame_out, mask, values = no_object.detect(frame)

    assert int(values["conf"]) == -1
    assert values["x"] is None
    assert int(values["relative_y_angle"]) == 0


def test_detect_donut():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    frame = cv2.imread(os.path.join(current_dir, "image_test", "donut.png"))
    frame = cv2.resize(frame, (640, 480))

    detector = ObjectDetection("donut", False)
    _, _, values = detector.detect(frame)

    assert int(values["relative_x_angle"]) == 3
    assert int(values["y"]) == 199


def test_detect_object_image_show(mocker):
    mock_imshow = mocker.patch('cv2.imshow')
    mock_waitKey = mocker.patch('cv2.waitKey')

    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    image_show = ObjectDetection("person", 0, show_img=True)
    image_show.detect(frame)

    assert mock_imshow.call_count == 1
    assert mock_waitKey.call_count == 1


def test_stop_image_show(mocker):
    mock_detection = mocker.Mock(spec=ObjectDetection)
    mock_detection.stop = ObjectDetection.stop.__get__(
        mock_detection)
    mock_detection.show_img = False
    mock_destroyAllWindows = mocker.patch('cv2.destroyAllWindows')
    mock_detection.stop()

    assert mock_destroyAllWindows.call_count == 0


def test_stop_not_image_show(mocker):
    mock_detection = mocker.Mock(spec=ObjectDetection)
    mock_detection.stop = ObjectDetection.stop.__get__(
        mock_detection)
    mock_detection.show_img = True
    mock_destroyAllWindows = mocker.patch('cv2.destroyAllWindows')
    mock_detection.stop()

    assert mock_destroyAllWindows.call_count == 1
