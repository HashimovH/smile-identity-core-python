__all__ = ["InvalidDataFormat", "ServerError", "VerificationFailed"]


class SmileIdError(Exception):
    def __init__(self, message):
        self.message = message


class InvalidDataFormat(SmileIdError, ValueError):
    pass


class ServerError(SmileIdError):
    pass


class VerificationFailed(SmileIdError):
    def __init__(self, data):
        self.message = data.get("ResultText")
        self.data = data
