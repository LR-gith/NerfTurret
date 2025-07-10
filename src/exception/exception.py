class AngleMissmatchException(Exception):
    """Raised when there is a mismatch between server and turret servo angles.

    This exception occurs when the absolute angle values returned by the server
    do not match the actual angles of the turret's servo motors.
    This could indicate a synchronization issue or incorrect angle calculation.

    Attributes:
        message (str): The error message.
    """
    pass


class EncodeImageException(Exception):
    """Raised when an image encoding operation fails.

    This exception occurs when OpenCV's imencode() function fails to encode
    an image into the specified format.

    Attributes:
        message (str): Fixed error message stating "Couldn't encode image."
    """


    def __init__(self):
        super().__init__("Couldn't encode image.")


class UnrecognizedDetectorException(Exception):
    """Raised when a detector is from an unknown class.

    This exception occurs when trying to create a new object of a detector
    based on the classname, but the class name isn't recognized as one of
    the classes from the detection package.

    Attributes:
        message (str): The error message.
    """
    pass


class ReconnectionFailedException(Exception):
    """Raised when the reconnection fails after multiple attempts.

    This exception occurs when trying to reconnect after connection
    to the server was lost. If the reconnection fails after multiple attempts,
    this exception is raised.

    Attributes:
        message (str): The error message.
    """
    pass


class CameraException(Exception):
    """Raised when the camera has an error.

    This exception occurs when the camera can't access the
    camera on the device and therefore can't collect images.

    Attributes:
        message (str): The error message.
    """
    pass
