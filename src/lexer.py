from shared import ConsoleLogger, Token, TokenType


class TextBuffer:
    def __init__(self, msg: str):
        self.msg = msg
        self.counter = 0

    def get_char(self):
        self.counter += 1
        if self.counter < len(self.msg):
            return self.msg[self.counter - 1]
        else:
            return "/n"


class Lexer():
    RESTRICTED_WORDS = ["fun", "if", "while", "else"]
    LETTERS = [
        "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N",
        "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "a", "b",
        "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p",
        "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"
    ]
    SPACE_ELEMENTS = ["\n", " "]
    SINGLE_CHAR_TOKENS = {
        "+": Token(TokenType.ADD_OPERATOR, "+"),
        "-": Token(TokenType.ADD_OPERATOR, "-"),
        "*": Token(TokenType.MULT_OPERATOR, "*"),
        "/": Token(TokenType.MULT_OPERATOR, "/"),
        "{": Token(TokenType.OPEN_BLOCK, "{"),
        "}": Token(TokenType.CLOSE_BLOCK, "}"),
        "(": Token(TokenType.OPEN_PAREN, "("),
        ")": Token(TokenType.CLOSE_PAREN, ")"),
        '"': Token(TokenType.QUOTATION_MARK, '"'),
    }

    def __init__(self, logger=ConsoleLogger, source=None):
        self.source = source
        self.logger = logger
        self.output = None
        self.buffered_char = "\n"

    def get_token(self) -> Token:
        if self.buffered_char is None:
            self.buffered_char = self.source.get_char()

        # read all of whitespaces between
        while (self.buffered_char in self.SPACE_ELEMENTS):
            self.buffered_char = self.source.get_char()

        if self.buffered_char in self.SINGLE_CHAR_TOKENS.keys():
            ret_val = self.buffered_char
            self.buffered_char = None
            return self.SINGLE_CHAR_TOKENS[ret_val]
