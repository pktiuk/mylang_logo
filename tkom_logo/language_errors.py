from .shared import Location


class BaseLanguageException(BaseException):
    def __init__(self, message, location: Location):
        self.location = location
        super().__init__(message)


class UnexpectedCharacterError(BaseLanguageException):
    def __init__(self, message, location: Location = None):
        super().__init__(message, location)


class ParseError(BaseLanguageException):
    def __init__(self, message, location: Location = None):
        super().__init__(message, location)


class SyntaxError(BaseLanguageException):
    def __init__(self, message, location: Location = None):
        super().__init__(message, location)


class LogoRuntimeError(BaseLanguageException):
    def __init__(self, message, location: Location = None):
        super().__init__(message, location)
