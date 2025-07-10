import pytest

from exception.exception import AngleMissmatchException
from exception.exception import CameraException
from exception.exception import EncodeImageException
from exception.exception import ReconnectionFailedException
from exception.exception import UnrecognizedDetectorException


def test_AngleMissmatchException():
    with pytest.raises(AngleMissmatchException) as exception:
        raise AngleMissmatchException("AngleMissmatchException test!")
    assert str(exception.value) == "AngleMissmatchException test!"


def test_EncodeImageException():
    with pytest.raises(EncodeImageException) as exception:
        raise EncodeImageException()
    assert str(exception.value) == "Couldn't encode image."


def test_UnrecognizedDetectorException():
    with pytest.raises(UnrecognizedDetectorException) as exception:
        raise UnrecognizedDetectorException(
            "UnrecognizedDetectorException test!")
    assert str(exception.value) == "UnrecognizedDetectorException test!"


def test_ReconnectionFailedException():
    with pytest.raises(ReconnectionFailedException) as exception:
        raise ReconnectionFailedException(
            "ReconnectionFailedException test!")
    assert str(exception.value) == "ReconnectionFailedException test!"


def test_CameraException():
    with pytest.raises(CameraException) as exception:
        raise CameraException("CameraException test!")
    assert str(exception.value) == "CameraException test!"
