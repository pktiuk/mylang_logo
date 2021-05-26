from .shared import Location


class UnexpectedCharacterError(BaseException):
    location: Location


class ParseError(BaseException):
    location: Location


class SyntaxError(BaseException):
    location: Location


class RuntimeError(BaseException):
    def __init__(self, message, element=None):
        self.location = None
        if element:
            self.location = element.location
        super().__init__(message, self.location)
