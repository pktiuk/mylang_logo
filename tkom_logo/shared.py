from enum import Enum, auto
from dataclasses import dataclass


class Logger(object):
    def __init__(self, *args):
        super(Logger, self).__init__(*args)

    def info(self, msg):
        raise NotImplementedError

    def warn(self, msg):
        raise NotImplementedError

    def error(self, msg):
        raise NotImplementedError

    def log(self, msg):
        raise NotImplementedError


class ConsoleLogger(Logger):
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    ENDC = '\033[0m'

    def __init__(self, *args):
        super(ConsoleLogger, self).__init__(*args)

    def info(self, msg):
        print(self.GREEN + msg + self.ENDC)

    def warn(self, msg):
        print(self.WARNING + msg + self.ENDC)

    def error(self, msg):
        print(self.ERROR + msg + self.ENDC)

    def log(self, msg):
        print(msg)


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

    def __init__(self, token: Token, children=[]):
        self.token = token
        self.children = children

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
