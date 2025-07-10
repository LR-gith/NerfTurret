class AngleMissmatchException(Exception):
    """
    Raised when there is a mismatch between server and turret servo angles.

    This exception occurs when the absolute angle values returned by the server
    do not match the actual angles of the turret's servo motors.
    This could indicate a synchronization issue or incorrect angle calculation.

    Attributes:
        message (str): The error message describing the angle discrepancy details.
    """
    pass


class EncodeImageException(Exception):
    def __init__(self):
        super().__init__("Couldn't encode image")


class UnrecognizedDetectorException(Exception): pass


class ReconnectionFailedException(Exception): pass


class CameraException(Exception): pass
