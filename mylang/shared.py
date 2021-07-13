from enum import Enum, auto
from dataclasses import dataclass


class Logger(object):
    def __init__(self, *args):
        super(Logger, self).__init__(*args)

    def info(self, msg, end="\n"):
        raise NotImplementedError

    def warn(self, msg, end="\n"):
        raise NotImplementedError

    def error(self, msg, end="\n"):
        raise NotImplementedError

    def log(self, msg, end="\n"):
        raise NotImplementedError


class ConsoleLogger(Logger):
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    ENDC = '\033[0m'

    def __init__(self, *args):
        super(ConsoleLogger, self).__init__(*args)

    def info(self, msg, end="\n"):
        print(self.GREEN + msg + self.ENDC)

    def warn(self, msg, end="\n"):
        print(self.WARNING + msg + self.ENDC)

    def error(self, msg, end="\n"):
        print(self.ERROR + msg + self.ENDC)

    def log(self, msg, end="\n"):
        print(msg, end=end)


class StringLogger(Logger):
    def __init__(self, *args):
        super(StringLogger, self).__init__(*args)
        self.out_string = ""

    def info(self, msg, end="\n"):
        self.out_string += "I: " + msg + end

    def warn(self, msg, end="\n"):
        self.out_string += "W: " + msg + end

    def error(self, msg, end="\n"):
        self.out_string += "E: " + msg + end

    def log(self, msg, end="\n"):
        self.out_string += msg + end


class TokenType(Enum):
    ASSIGNMENT_OPERATOR = auto()
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
    FIELD_OPERATOR = auto()
    FUN_OPERATOR = auto()
    COMMA = auto()


@dataclass
class Location:
    line: int
    char_number: int

    def __init__(self, line, char_number):
        self.line = line
        self.char_number = char_number


@dataclass
class Token(object):
    symbol_type: TokenType
    value: str
    location: Location

    def __init__(self,
                 token_type: TokenType,
                 input_value: str,
                 location: Location = None):
        if type(token_type) != TokenType:
            raise TypeError

        self.value = input_value
        self.symbol_type = token_type
        self.location = location


@dataclass
class ParserNode(object):
    token: Token
    children: list

    def __init__(self, token: Token, children=None):
        self.token = token
        self.children = children if children else []

    def __str__(self, level=0):
        ret = "\t" * level
        ret += f'{self.token.value} type: {self.token.symbol_type} Loc: {self.token.location} \n'
        for child in self.children:
            ret += child.__str__(level + 1)
        return ret

    def get_depth(self) -> int:
        if len(self.children):
            return 1 + max(x.get_depth() for x in self.children)
        else:
            return 0
