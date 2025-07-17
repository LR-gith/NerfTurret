import os
import sys

import cv2
import numpy as np
import pytest
from webcolors import IntegerRGB

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.detection.color_detection import ColorDetection


def test_init_valid_color_name():
    valid_color_name = ColorDetection("darkSlateBlue", 10, False)

    assert valid_color_name.target_class == IntegerRGB(72, 61, 139)
    assert (valid_color_name.lower_rgb == [62, 51, 129]).all()


def test_init_valid_color_array():
    valid_color_array = ColorDetection(["#ffffff", "#000000"], 0, False)

    assert valid_color_array.target_class == IntegerRGB(127, 127, 127)


def test_init_invalid_color_range():
    with pytest.raises(AttributeError):
        ColorDetection("black", -2, False)


def test_detect_blue_square_in_middle():
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.rectangle(frame, (360, 280), (280, 200), (255, 0, 0), -1)
    square_middle = ColorDetection("blue", 0, False)
    frame_out, mask, values = square_middle.detect(frame)

    assert int(values["relative_x_angle"]) == 0
    assert int(values["relative_y_angle"]) == 0


def test_detect_blue_square_on_left_side():
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.rectangle(frame, (0, 0), (320, 240), (255, 0, 0), -1)
    square_left = ColorDetection("blue", 0, False)
    frame_out, mask, values = square_left.detect(frame)

    assert int(values["relative_x_angle"]) == -22
    assert int(values["relative_y_angle"]) == 17


def test_detect_blue_square_too_small():
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.rectangle(frame, (340, 250), (344, 254), (255, 0, 0), -1)
    too_small_square = ColorDetection("blue", 0, False)
    frame_out, mask, values = too_small_square.detect(frame)

    assert int(values["conf"]) == -1
    assert values["x"] is None
    assert int(values["relative_y_angle"]) == 0


def test_detect_no_object():
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    no_object = ColorDetection("blue", 0, False)
    frame_out, mask, values = no_object.detect(frame)

    assert int(values["conf"]) == -1
    assert values["x"] is None
    assert int(values["relative_y_angle"]) == 0


def test_detect_object_image_show(mocker):
    mock_imshow = mocker.patch('cv2.imshow')
    mock_waitKey = mocker.patch('cv2.waitKey')

    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    image_show = ColorDetection("blue", 0, False, show_img=True)
    image_show.detect(frame)

    assert mock_imshow.call_count == 2
    assert mock_waitKey.call_count == 1


def test_set_rgb_bounds_invalid_type(mocker):
    mock_detection = mocker.Mock(spec=ColorDetection)
    mock_detection.color_range = 20
    mock_detection.set_rgb_bounds = ColorDetection.set_rgb_bounds.__get__(
        mock_detection)
    rgb_color = (20, 20)
    with pytest.raises(ValueError):
        mock_detection.set_rgb_bounds(rgb_color)


def test_set_rgb_bounds_lower_bound_min(mocker):
    mock_detection = mocker.Mock(spec=ColorDetection)
    mock_detection.color_range = 30
    mock_detection.set_rgb_bounds = ColorDetection.set_rgb_bounds.__get__(
        mock_detection)
    rgb_color = (10, 0, 40)
    lower, _ = mock_detection.set_rgb_bounds(rgb_color)

    assert (lower == (0, 0, 10)).all


def test_set_rgb_bounds_upper_bound_max(mocker):
    mock_detection = mocker.Mock(spec=ColorDetection)
    mock_detection.color_range = 50
    mock_detection.set_rgb_bounds = ColorDetection.set_rgb_bounds.__get__(
        mock_detection)
    rgb_color = (255, 250, 50)
    _, upper = mock_detection.set_rgb_bounds(rgb_color)

    assert (upper == (255, 255, 100)).all


def test_color_mean_valid_array(mocker):
    mock_detection = mocker.Mock(spec=ColorDetection)
    mock_detection.color_mean = ColorDetection.color_mean.__get__(
        mock_detection)
    hex_colors = ["#ffffff", "#000000"]
    (rgb_red, rgb_green, rgb_blue) = mock_detection.color_mean(hex_colors)

    assert ((rgb_red, rgb_green, rgb_blue) == (127, 127, 127))


def test_color_mean_valid_string(mocker):
    mock_detection = mocker.Mock(spec=ColorDetection)
    mock_detection.color_mean = ColorDetection.color_mean.__get__(
        mock_detection)
    hex_colors = "#000000"
    rgb_red, rgb_green, rgb_blue = mock_detection.color_mean(hex_colors)

    assert ((rgb_red, rgb_green, rgb_blue) == (0, 0, 0))


def test_color_mean_invalid_type(mocker):
    mock_detection = mocker.Mock(spec=ColorDetection)
    mock_detection.color_mean = ColorDetection.color_mean.__get__(
        mock_detection)
    hex_colors = (0, 0, 0)

    with pytest.raises(ValueError):
        mock_detection.color_mean(hex_colors)


def test_stop_image_show(mocker):
    mock_detection = mocker.Mock(spec=ColorDetection)
    mock_detection.stop = ColorDetection.stop.__get__(
        mock_detection)
    mock_detection.show_img = False
    mock_destroyAllWindows = mocker.patch('cv2.destroyAllWindows')
    mock_detection.stop()

    assert mock_destroyAllWindows.call_count == 0


def test_stop_not_image_show(mocker):
    mock_detection = mocker.Mock(spec=ColorDetection)
    mock_detection.stop = ColorDetection.stop.__get__(
        mock_detection)
    mock_detection.show_img = True
    mock_destroyAllWindows = mocker.patch('cv2.destroyAllWindows')
    mock_detection.stop()

    assert mock_destroyAllWindows.call_count == 1
