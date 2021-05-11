from shared import Location


class UnexpectedCharacterError(BaseException):
    location: Location


class ParseError(BaseException):
    location: Location


class SyntaxError(BaseException):
    location: Location