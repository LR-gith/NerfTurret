class AngleMissmatchException(Exception): pass
class EncodeImageException(Exception):
    def __init__(self):
        super().__init__("Couldn't encode image")
class UnrecognizedDetectorException(Exception): pass
class ReconnectionFailedException(Exception): pass