import json.decoder
import os
import sys

import pytest
import requests

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import src.exception.exception
from src.exception.exception import EncodeImageException
from src.exception.exception import ReconnectionFailedException
from src.turret import client


@pytest.fixture
def request_post_mock(mocker):
    return mocker.patch('src.turret.client.requests.post')


@pytest.fixture
def request_get_mock(mocker):
    return mocker.patch('src.turret.client.requests.get')


@pytest.fixture
def time_sleep_mock(mocker):
    return mocker.patch('src.turret.client.time.sleep')


@pytest.fixture
def ping_mock(mocker):
    return mocker.patch('src.turret.client.ping')


@pytest.fixture
def reconnect_mock(mocker):
    return mocker.patch('src.turret.client.reconnect')


@pytest.fixture
def reconnect_success_mock(reconnect_mock):
    reconnect_mock.return_value = True


@pytest.fixture
def reconnect_failed_mock(reconnect_mock):
    reconnect_mock.side_effect = ReconnectionFailedException


@pytest.fixture
def to_bytes_mock(mocker):
    to_bytes_mock = mocker.Mock()
    to_bytes_mock.tobytes.return_value = "image to bytes"
    return to_bytes_mock


@pytest.fixture
def io_mock(mocker):
    io_mock = mocker.patch("src.turret.client.io.BytesIO")
    io_mock.return_value = "buffered image"


@pytest.fixture
def response_mock(mocker):
    return mocker.Mock()


def test_initialize_connection_success(time_sleep_mock, ping_mock):
    ping_mock.return_value = True

    assert client.initialize_connection() == True


def test_initialize_connection_failure(time_sleep_mock, ping_mock):
    ping_mock.return_value = False

    assert client.initialize_connection() == False


def test_reconnect_success(time_sleep_mock, ping_mock):
    ping_mock.return_value = True

    assert client.reconnect() == True


def test_reconnect_failure(time_sleep_mock, ping_mock):
    ping_mock.return_value = False

    with pytest.raises(ReconnectionFailedException):
        client.reconnect()


def test_print_detection_response_helper_with_print(response_mock, capsys):
    response_mock.json.return_value = {"test one": "test print this",
                                       "test two": "test print this too"}
    client.CURRENT_ITERATION = 1
    client.PRINT_ITERATION = 1
    client.print_detection_response_helper(response_mock)
    captured_print = capsys.readouterr()

    assert "test one: test print this, test two: test print this too" in captured_print.out


def test_print_detection_response_helper_without_print(response_mock, capsys):
    response_mock.json.return_value = {"test one": "test print this",
                                       "test two": "test print this too"}
    client.CURRENT_ITERATION = 1
    client.PRINT_ITERATION = 2
    client.print_detection_response_helper(response_mock)
    captured_print = capsys.readouterr()

    assert "test one: test print this, test two: test print this too" not in captured_print.out


def test_update_object_detection_success(mocker, request_post_mock,
                                         to_bytes_mock,
                                         io_mock):
    imencode_mock = mocker.patch("cv2.imencode")
    imencode_mock.return_value = True, to_bytes_mock

    assert client.update_object_detection("frame", None) is True


def test_update_object_detection_encode_image_failure(mocker):
    imencode_mock = mocker.patch("cv2.imencode")
    imencode_mock.return_value = False, "encoded frame"

    with pytest.raises(EncodeImageException):
        client.update_object_detection("frame", None)


def test_update_object_detection_post_and_reconnect_failure(mocker,
                                                            request_post_mock,
                                                            reconnect_mock,
                                                            reconnect_failed_mock,
                                                            to_bytes_mock,
                                                            io_mock):
    imencode_mock = mocker.patch("cv2.imencode")
    imencode_mock.return_value = True, to_bytes_mock
    request_post_mock.side_effect = requests.exceptions.ConnectionError()

    with pytest.raises(src.exception.exception.ReconnectionFailedException):
        client.update_object_detection("frame", None)

    assert reconnect_mock.call_count == 1


def test_update_object_detection_posts_failed_reconnect_success(mocker,
                                                                request_post_mock,
                                                                reconnect_success_mock,
                                                                to_bytes_mock,
                                                                io_mock):
    imencode_mock = mocker.patch("cv2.imencode")
    imencode_mock.return_value = True, to_bytes_mock
    request_post_mock.side_effect = requests.exceptions.ConnectionError()
    create_new_buffer_mock = mocker.patch("src.turret.client.create_new_buffer")
    create_new_buffer_mock.return_value = "byted image"

    with pytest.raises(requests.exceptions.ConnectionError):
        client.update_object_detection("frame", None)

    assert request_post_mock.call_count == 2


def test_update_color_detection_success(mocker, request_post_mock,
                                        to_bytes_mock,
                                        io_mock):
    to_bytes_mock.tobytes.return_value = "fake_frame_bytes"
    imencode_mock = mocker.patch("cv2.imencode")
    imencode_mock.return_value = True, to_bytes_mock

    assert client.update_color_detection("frame", "mask", None) is True


def test_update_color_detection_encode_image_failure(mocker):
    imencode_mock = mocker.patch("cv2.imencode")
    imencode_mock.return_value = False, "encoded frame"

    with pytest.raises(EncodeImageException):
        client.update_color_detection("frame", "mask", None)


def test_update_color_detection_post_and_reconnect_failure(mocker,
                                                           request_post_mock,
                                                           reconnect_mock,
                                                           reconnect_failed_mock,
                                                           to_bytes_mock,
                                                           io_mock):
    imencode_mock = mocker.patch("cv2.imencode")
    imencode_mock.return_value = True, to_bytes_mock
    request_post_mock.side_effect = requests.exceptions.ConnectionError()

    with pytest.raises(src.exception.exception.ReconnectionFailedException):
        client.update_color_detection("frame", "mask", None)

    assert reconnect_mock.call_count == 1


def test_update_color_detection_both_posts_failed_reconnect_success(mocker,
                                                                    request_post_mock,
                                                                    reconnect_success_mock,
                                                                    to_bytes_mock,
                                                                    io_mock):
    imencode_mock = mocker.patch("cv2.imencode")
    imencode_mock.return_value = True, to_bytes_mock
    request_post_mock.side_effect = requests.exceptions.ConnectionError()
    create_new_buffer_mock = mocker.patch("src.turret.client.create_new_buffer")
    create_new_buffer_mock.return_value = "byted image"

    with pytest.raises(requests.exceptions.ConnectionError):
        client.update_color_detection("frame", "mask", None)

    assert request_post_mock.call_count == 2


def test_calculate_detection_success_with_print(request_post_mock,
                                                response_mock,
                                                capsys):
    response_mock.status_code = 200
    response_mock.json.return_value = {"values": {"data": "test with print"}}
    request_post_mock.return_value = response_mock

    values = client.calculate_detection("data", "image")
    captured_print = capsys.readouterr()

    assert "data: test with print" in captured_print.out
    assert values == {"data": "test with print"}


def test_calculate_detection_reconnect_success(mocker, request_post_mock,
                                               response_mock,
                                               reconnect_success_mock):
    response_mock.status_code = 200
    response_mock.json.return_value = {"values": {"data": "test success"}}
    create_new_buffer_mock = mocker.patch("src.turret.client.create_new_buffer")
    create_new_buffer_mock.return_value = "new buffered image"
    request_post_mock.side_effect = [requests.exceptions.ConnectionError,
                                     response_mock]

    values = client.calculate_detection("data", {
        'image': ('frame.jpg', "image bytes", 'image/jpeg')})

    assert values == {"data": "test success"}
    assert create_new_buffer_mock.call_count == 1


def test_calculate_detection_invalid_https_code(request_post_mock,
                                                response_mock):
    response_mock.status_code = 500
    request_post_mock.return_value = response_mock

    with pytest.raises(SystemError):
        client.calculate_detection("data", "image")


def test_calculate_detection_invalid_json(request_post_mock,
                                          response_mock):
    response_mock.status_code = 200
    response_mock.json.side_effect = json.decoder.JSONDecodeError("msg", "doc",
                                                                  1)
    request_post_mock.return_value = response_mock

    with pytest.raises(ValueError):
        client.calculate_detection("data", "image")


def test_update_only_image_success(mocker, request_post_mock, to_bytes_mock,
                                   io_mock):
    imencode_mock = mocker.patch("cv2.imencode")
    imencode_mock.return_value = True, to_bytes_mock

    assert client.update_only_image("frame") is True


def test_update_only_image_encode_image_failure(mocker):
    imencode_mock = mocker.patch("cv2.imencode")
    imencode_mock.return_value = False, "encoded frame"

    with pytest.raises(EncodeImageException):
        client.update_only_image("frame")


def test_update_only_image_post_and_reconnect_failure(mocker, request_post_mock,
                                                      reconnect_mock,
                                                      reconnect_failed_mock,
                                                      to_bytes_mock, io_mock):
    imencode_mock = mocker.patch("cv2.imencode")
    imencode_mock.return_value = True, to_bytes_mock
    request_post_mock.side_effect = requests.exceptions.ConnectionError()

    with pytest.raises(src.exception.exception.ReconnectionFailedException):
        client.update_only_image("frame")

    assert reconnect_mock.call_count == 1


def test_update_only_image_both_posts_failed_reconnect_success(mocker,
                                                               request_post_mock,
                                                               reconnect_success_mock,
                                                               to_bytes_mock,
                                                               io_mock):
    imencode_mock = mocker.patch("cv2.imencode")
    imencode_mock.return_value = True, to_bytes_mock
    request_post_mock.side_effect = requests.exceptions.ConnectionError()
    create_new_buffer_mock = mocker.patch("src.turret.client.create_new_buffer")
    create_new_buffer_mock.return_value = "byted image"

    with pytest.raises(requests.exceptions.ConnectionError):
        client.update_only_image("frame")

    assert request_post_mock.call_count == 2


def test_get_color_selection_post_and_reconnect_failed(reconnect_failed_mock,
                                                       request_get_mock):
    request_get_mock.side_effect = requests.exceptions.ConnectionError

    with pytest.raises(ReconnectionFailedException):
        client.get_color_selections()


def test_get_color_selection_reconnect_success(reconnect_mock,
                                               request_get_mock,
                                               response_mock):
    response_mock.json.return_value = {"status": "ok", "colors": "blue"}
    request_get_mock.side_effect = [
        requests.exceptions.ConnectionError, response_mock]

    success, colors = client.get_color_selections()

    assert success is True
    assert colors == "blue"


def test_get_color_selection_invalid_status(reconnect_mock,
                                            request_get_mock,
                                            response_mock):
    response_mock.json.return_value = {"status": "fail", "colors": "blue"}
    request_get_mock.return_value = response_mock

    success, colors = client.get_color_selections()

    assert success is False
    assert colors is None


def test_clear_color_selections_reconnect_failed(reconnect_failed_mock,
                                                 request_get_mock):
    request_get_mock.side_effect = requests.exceptions.ConnectionError

    with pytest.raises(ReconnectionFailedException):
        client.clear_color_selections()


def test_clear_color_selections_reconnect_success(reconnect_success_mock,
                                                  request_get_mock):
    request_get_mock.side_effect = requests.exceptions.ConnectionError

    with pytest.raises(requests.exceptions.ConnectionError):
        client.clear_color_selections()


def test_clear_color_selections_success(response_mock, request_get_mock):
    response_mock.json.return_value = {"status": "", "colors": ""}
    request_get_mock.return_value = response_mock

    assert client.clear_color_selections() is True


def test_clear_color_selection_failure(response_mock, request_get_mock):
    response_mock.json.return_value = {"status": "", "colors": "blue"}
    request_get_mock.return_value = response_mock

    assert client.clear_color_selections() is False


def test_redirect_to_color_selection_reconnect_failed(reconnect_failed_mock,
                                                      request_get_mock):
    request_get_mock.side_effect = requests.exceptions.ConnectionError

    with pytest.raises(ReconnectionFailedException):
        client.redirect_to_color_selection()


def test_redirect_to_color_selection_reconnect_success(reconnect_success_mock,
                                                       request_get_mock):
    request_get_mock.side_effect = requests.exceptions.ConnectionError

    with pytest.raises(requests.exceptions.ConnectionError):
        client.redirect_to_color_selection()


def test_redirect_to_color_selection_success(response_mock, request_get_mock):
    response_mock.json.return_value = {"status": "redirected"}
    request_get_mock.return_value = response_mock

    assert client.redirect_to_color_selection() is True


def test_redirect_to_color_selection_failed(response_mock, request_get_mock):
    response_mock.json.return_value = {"status": "anything but redirected"}
    request_get_mock.return_value = response_mock

    assert client.redirect_to_color_selection() is False


def test_log_to_server_success(request_post_mock):
    assert client.log_to_server("message") is True


def test_log_to_server_failed(request_post_mock, reconnect_failed_mock):
    request_post_mock.side_effect = requests.exceptions.ConnectionError

    with pytest.raises(ReconnectionFailedException):
        client.log_to_server("message")


def test_log_to_server_redirect_success(request_post_mock,
                                        reconnect_success_mock):
    request_post_mock.side_effect = requests.exceptions.ConnectionError

    with pytest.raises(requests.exceptions.ConnectionError):
        client.log_to_server("message")


def test_ping_timeout_failure(request_get_mock):
    request_get_mock.side_effect = TimeoutError

    assert client.ping() is False


def test_ping_connection_failure(request_get_mock):
    request_get_mock.side_effect = requests.exceptions.ConnectionError()

    assert client.ping() is False


def test_ping_invalid_response(response_mock, request_get_mock):
    response_mock.content.decode.return_value = "invalid"
    request_get_mock.return_value = response_mock

    assert client.ping() is False


def test_ping_valid_response(response_mock, request_get_mock):
    response_mock.content.decode.return_value = "pong"
    request_get_mock.return_value = response_mock

    assert client.ping() is True


def test_set_print_iteration():
    client.set_print_iteration(21)
    client.set_print_iteration(1)

    assert client.PRINT_ITERATION == 1
