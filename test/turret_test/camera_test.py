import os
import sys

import numpy as np
import pytest

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.exception.exception import CameraException
from src.turret.camera import Camera


def test_init_success(mocker):
    mock_cap = mocker.MagicMock()
    mock_cap.read.return_value = (True, "mock_frame")
    mock_cap.isOpened.return_value = True
    mocker.patch("src.turret.camera.cv2.VideoCapture", return_value=mock_cap)
    camera = Camera()

    assert camera.frame == "mock_frame"
    assert camera.thread.is_alive()

    camera.running = False
    camera.thread.join()


def test_init_read_failed(mocker):
    mock_cap = mocker.MagicMock()
    mock_cap.read.return_value = (False, "mock_frame")
    mocker.patch("src.turret.camera.cv2.VideoCapture", return_value=mock_cap)

    with pytest.raises(CameraException):
        Camera()


def test_init_isOpened_failed(mocker):
    mock_cap = mocker.MagicMock()
    mock_cap.read.return_value = (True, "mock_frame")
    mock_cap.isOpened.return_value = False
    mocker.patch("src.turret.camera.cv2.VideoCapture", return_value=mock_cap)

    with pytest.raises(CameraException):
        Camera()


def test_update_success(mocker):
    mock_cap = mocker.MagicMock()
    mock_cap.isOpened.return_value = True
    mock_cap.read.side_effect = [
        (True, "initial"),
        (True, "frame")
    ]
    mocker.patch("src.turret.camera.cv2.VideoCapture", return_value=mock_cap)
    camera = Camera()

    with camera.lock:
        assert camera.frame in ["initial", "frame"]

    camera.running = False
    camera.thread.join()


def test_update_not_running(mocker):
    mock_cap = mocker.MagicMock()
    mock_cap.isOpened.return_value = True
    mock_cap.read.side_effect = [(True, "initial"), (True, "frame")]
    mocker.patch("src.turret.camera.cv2.VideoCapture", return_value=mock_cap)
    thread_mock = mocker.MagicMock()
    mocker.patch("src.turret.camera.threading.Thread", return_value=thread_mock)
    camera = Camera()
    camera.running = False
    camera.update()

    mock_cap.read.assert_called_once()
    assert camera.frame == "initial"


def test_read(mocker):
    mock_cap = mocker.MagicMock()
    mock_cap.isOpened.return_value = True
    test_frame = np.array([[[0, 0, 0], [0, 0, 0]], [[0, 0, 0], [0, 0, 0]]])
    mock_cap.read.side_effect = [(True, test_frame),
                                 (True, "frame")]
    mocker.patch("src.turret.camera.cv2.VideoCapture", return_value=mock_cap)
    thread_mock = mocker.MagicMock()
    mocker.patch("src.turret.camera.threading.Thread", return_value=thread_mock)
    camera = Camera()
    ret, frame = camera.read()

    assert (camera.frame == frame).all()
    assert camera.ret == ret


def test_stop(mocker):
    mock_cap = mocker.MagicMock()
    mock_cap.isOpened.return_value = True
    mock_cap.read.side_effect = [(True, "initial"), (True, "frame")]
    mocker.patch("src.turret.camera.cv2.VideoCapture", return_value=mock_cap)
    camera = Camera()
    camera.stop()

    assert not camera.thread.is_alive()
    mock_cap.release.assert_called_once()
