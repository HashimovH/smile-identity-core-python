__all__ = ["InvalidDataFormat", "ServerError"]


class SmileIdError(Exception):
    def __init__(self, message):
        self.message = message


class InvalidDataFormat(SmileIdError, ValueError):
    pass


class ServerError(SmileIdError):
    pass
