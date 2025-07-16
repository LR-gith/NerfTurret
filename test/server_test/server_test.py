import io
import os
import sys

import cv2
import numpy as np
import pytest

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.server import server
from src.server.server import app


@pytest.fixture
def client():
    app.debug = True
    app.config['PROPAGATE_EXCEPTIONS'] = False
    with app.test_client() as client:
        yield client


@pytest.fixture
def test_values():
    return {
        'conf': 'test conf',
        'x': 'test x',
        'y': 'test y',
        'relative_x_angle': 'test relative_x_angle',
        'relative_y_angle': 'test relative_y_angle',
        'absolut_x_angle': 'test absolut_x_angle',
        'absolut_y_angle': 'test absolut_y_angle',
    }


def test_homepage(client):
    response = client.get('/')

    assert response.status_code == 200
    assert response.mimetype == "text/html"


def test_color_selector(client):
    response = client.get('/colorSelector')

    assert response.status_code == 200
    assert response.mimetype == "text/html"


def test_ping(client):
    response = client.get('/ping')

    assert response.text == "pong"


def test_update_object_detection_success(mocker, client, test_values):
    img = np.zeros((100, 100), dtype=np.uint8)
    success, encoded_image = cv2.imencode('.jpg', img)
    test_image = io.BytesIO(encoded_image.tobytes())
    socketio_emit_mock = mocker.patch("src.server.server.socketio.emit")

    response = client.post(
        '/updateObjectDetection',
        data={**test_values, 'image': (test_image, 'image.jpg')},
        content_type='multipart/form-data'
    )

    assert response.json == test_values
    assert response.status_code == 200
    assert socketio_emit_mock.call_count == 1


def test_update_object_detection_image_missing(client, test_values):
    response = client.post('/updateObjectDetection', data=test_values)

    assert response.json == {"error": "Missing image in request"}
    assert response.status_code == 400


def test_update_color_detection_success(mocker, client, test_values):
    img = np.zeros((100, 100), dtype=np.uint8)
    success, encoded_image = cv2.imencode('.jpg', img)
    test_image = io.BytesIO(encoded_image.tobytes())
    test_mask = io.BytesIO(encoded_image.tobytes())
    socketio_emit_mock = mocker.patch("src.server.server.socketio.emit")

    response = client.post(
        '/updateColorDetection',
        data={**test_values, 'image': (test_image, 'image.jpg'),
              'mask': (test_mask, 'mask.jpg')},
        content_type='multipart/form-data'
    )

    assert response.json == test_values
    assert response.status_code == 200
    assert socketio_emit_mock.call_count == 1


def test_calculate_detection_invalid_detection_class(client):
    img = np.zeros((100, 100), dtype=np.uint8)
    success, encoded_image = cv2.imencode('.jpg', img)
    test_image = io.BytesIO(encoded_image.tobytes())
    calc_detect_values = {
        'website_running': 'True',
        'detector_class': 'Invalid',
        'detector_target_class': 'person',
        'detector_color_range': '0',
        'detector_show_img': 'False',
        'absolut_x_angle': '90',
        'absolut_y_angle': '90',
    }

    response = client.post(
        '/calculateDetection',
        data={**calc_detect_values, 'image': (test_image, 'image.jpg')},
        content_type='multipart/form-data'
    )

    assert response.status_code == 500


def test_calculate_detection_object(mocker, client):
    img = np.zeros((100, 100), dtype=np.uint8)
    success, encoded_image = cv2.imencode('.jpg', img)
    test_image = io.BytesIO(encoded_image.tobytes())
    mocker.patch("src.server.server.socketio.emit")
    calc_detect_values = {
        'website_running': 'True',
        'detector_class': 'ObjectDetection',
        'detector_target_class': 'person',
        'detector_color_range': '0',
        'detector_show_img': 'False',
        'absolut_x_angle': '90',
        'absolut_y_angle': '90',
    }

    response = client.post(
        '/calculateDetection',
        data={**calc_detect_values, 'image': (test_image, 'image.jpg')},
        content_type='multipart/form-data'
    )

    assert response.status_code == 200
    assert response.json == {'values':
                                 {"conf": -1,
                                  "x": None, "y": None,
                                  "relative_x_angle": 0,
                                  "relative_y_angle": 0,
                                  "absolut_x_angle": 90,
                                  "absolut_y_angle": 90}}


def test_calculate_detection_color(mocker, client):
    img = np.zeros((100, 100), dtype=np.uint8)
    success, encoded_image = cv2.imencode('.jpg', img)
    test_image = io.BytesIO(encoded_image.tobytes())
    mocker.patch("src.server.server.socketio.emit")
    calc_detect_values = {
        'website_running': 'True',
        'detector_class': 'ColorDetection',
        'detector_target_class': '#ffffff',
        'detector_color_range': '1',
        'detector_show_img': 'False',
        'absolut_x_angle': '90',
        'absolut_y_angle': '90',
    }

    response = client.post(
        '/calculateDetection',
        data={**calc_detect_values, 'image': (test_image, 'image.jpg')},
        content_type='multipart/form-data'
    )

    assert response.status_code == 200
    assert response.json == {'values':
                                 {"conf": -1,
                                  "x": None, "y": None,
                                  "relative_x_angle": 0,
                                  "relative_y_angle": 0,
                                  "absolut_x_angle": 90,
                                  "absolut_y_angle": 90}}


def test_update_only_image_missing_image(client):
    response = client.post('/updateOnlyImage',
                           data={"not image": "test"})

    assert response.json == {"error": "Missing image in request"}
    assert response.status_code == 400


def test_update_only_image(client):
    img = np.zeros((100, 100), dtype=np.uint8)
    success, encoded_image = cv2.imencode('.jpg', img)
    test_image = io.BytesIO(encoded_image.tobytes())

    response = client.post('/updateOnlyImage',
                           data={'image': (test_image, 'image.jpg')}, )

    assert response.json == {"status": "ok"}
    assert response.status_code == 200


def test_update_color_detection_image_missing(client, test_values):
    response = client.post('/updateColorDetection', data=test_values)

    assert response.json == {
        "error": "Missing either the image, the mask or both in request"}
    assert response.status_code == 400


def test_get_color_selection_list_status_waiting(client):
    response = client.get('/get_color_selection_list')

    assert response.json == {"status": "waiting", "colors": []}


def test_get_color_selection_list_status_ok(client):
    server.color_selections["colors"].append("#ffffff")
    print(server.color_selections)

    response = client.get('/get_color_selection_list')

    assert response.json == {"status": "ok", "colors": ["#ffffff"]}


def test_clear_color_selections(client):
    server.color_selections["colors"].append("#000000")
    server.color_selections["status"] = "test"

    response = client.get('/clear_color_selection')

    assert response.json == {"status": "", "colors": []}


def test_update_color_selections_missing_colors(client):
    response = client.post('/updateColorSelections',
                           json={"not colors": "test"})

    assert response.json == {"error": "Missing color data"}
    assert response.status_code == 400


def test_update_color_selections(client):
    response = client.post('/updateColorSelections',
                           json={"colors": ["#232323", "#121212"]})

    assert response.json == {"status": "ok"}
    assert server.color_selections["colors"] == ["#232323", "#121212"]


def test_redirect_to_color_selection_success(mocker, client):
    mocker.patch("src.server.server.socketio.emit")

    response = client.get('/redirectToColorSelection')

    assert response.json == {"status": "redirected"}


def test_get_image_no_image_available(client):
    server.current_image = None
    response = client.get('/get_image')

    assert response.text == "No image available"
    assert response.status_code == 404


def test_get_image_imencode_failed(mocker, client):
    server.current_image = "image"
    imencode_mock = mocker.patch("cv2.imencode")
    imencode_mock.return_value = False, None

    response = client.get('/get_image')

    assert response.text == "Could not encode image"
    assert response.status_code == 500


def test_get_mask_no_image_available(client):
    server.current_mask = None
    response = client.get('/get_mask')

    assert response.text == "No mask available"
    assert response.status_code == 404


def test_get_image_success(client):
    server.current_image = np.zeros((100, 100), dtype=np.uint8)

    response = client.get('/get_image')
    assert response.status_code == 200
    assert response.content_type == 'image/jpeg'


def test_get_mask_imencode_failed(mocker, client):
    server.current_mask = "image"
    imencode_mock = mocker.patch("cv2.imencode")
    imencode_mock.return_value = False, None

    response = client.get('/get_mask')

    assert response.text == "Could not encode image"
    assert response.status_code == 500


def test_get_mask_success(client):
    server.current_mask = np.zeros((100, 100), dtype=np.uint8)

    response = client.get('/get_mask')
    assert response.status_code == 200
    assert response.content_type == 'image/jpeg'


def test_log_message_valid(mocker, client):
    mocker.patch("src.server.server.socketio.emit")

    response = client.post('/log', json={"message": "test message"})

    assert response.status_code == 200
    assert response.json == {"message": "test message"}
