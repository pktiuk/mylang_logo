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
        "\n": Token(TokenType.EOL, "\n"),
    }

    def __init__(self, logger=ConsoleLogger, source=None):
        self.source = source
        self.logger = logger
        self.output = None
        self.buffered_char = "\n"

    def get_token(self) -> Token:
        token_string = self._get_token_string()
        if token_string in self.RESTRICTED_WORDS:
            if token_string == "fun":
                return Token(TokenType.FUN, token_string)
            elif token_string == "if":
                return Token(TokenType.IF, token_string)
            #TODO the rest
        else:
            pass

    def _get_token_string(self):
        if self.buffered_char is None:
            self.buffered_char = self.source.get_char()

        ending_characters = []
        while (self.buffered_char == " "):
            self.buffered_char = self.source.get_char()

        if self.buffered_char in self.SINGLE_CHAR_TOKENS:
            ret_val = self.buffered_char
            self.buffered_char = None
            return ret_val
