from enum import Enum, auto


class TokenType(Enum):
    EOF = auto()
    EOL = auto()
    FUN = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    OPEN_BLOCK = auto()
    CLOSE_BLOCK = auto()
    OPEN_PAREN = auto()
    CLOSE_PAREN = auto()
    ADD_OPERATOR = auto()
    MULT_OPERATOR = auto()
    UNARY_OPERATOR = auto()
    OR_OPERATOR = auto()
    AND_OPERATOR = auto()
    COMP_OPERATOR = auto()
    CONST = auto()
    IDENTIFIER = auto()


class Location:
    def __init__(self, line, char_number):
        self.line = line
        self.char_number = char_number


class Token(object):
    def __init__(self,
                 token_type: TokenType,
                 input_string: str,
                 location: Location = None):
        self.value = input_string
        self.type = token_type
        self.location = location
