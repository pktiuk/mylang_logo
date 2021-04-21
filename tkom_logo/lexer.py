from shared import ConsoleLogger, Token, TokenType


class UnexpectedCharacterError(BaseException):
    pass


class ParseError(BaseException):
    pass


class Lexer():
    RESTRICTED_WORDS = ["fun", "if", "while", "else"]
    LETTERS = [
        "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N",
        "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "a", "b",
        "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p",
        "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"
    ]
    NUMBERS = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    WHITESPACE_ELEMENTS = ["\n", " "]

    # Tokens consisting of only one token which cannot be parts of other tokens
    SINGLE_CHAR_TOKENS = {
        "+": Token(TokenType.ADD_OPERATOR, "+"),
        "-": Token(TokenType.ADD_OPERATOR, "-"),
        "*": Token(TokenType.MULT_OPERATOR, "*"),
        "/": Token(TokenType.MULT_OPERATOR, "/"),
        "{": Token(TokenType.OPEN_BLOCK, "{"),
        "}": Token(TokenType.CLOSE_BLOCK, "}"),
        "(": Token(TokenType.OPEN_PAREN, "("),
        ")": Token(TokenType.CLOSE_PAREN, ")"),
    }

    # Tokens consisting of two tokens, which can't be part of
    # identifier or const value
    TWO_CHAR_TOKENS = {
        "||": Token(TokenType.OR_OPERATOR, "||"),
        "&&": Token(TokenType.AND_OPERATOR, "&&"),
        "==": Token(TokenType.COMP_OPERATOR, "=="),
        "<=": Token(TokenType.COMP_OPERATOR, "<="),
        ">=": Token(TokenType.COMP_OPERATOR, ">="),
        "!=": Token(TokenType.COMP_OPERATOR, "!="),
    }

    RESTRICTED_IDENTIFIERS = {
        "fun": Token(TokenType.FUN, "fun"),
        "while": Token(TokenType.WHILE, "while"),
        "if": Token(TokenType.IF, "if"),
        "else": Token(TokenType.ELSE, "else"),
    }

    def __init__(self, logger=ConsoleLogger, source=None):
        self.source = source
        self.logger = logger
        self.output = None
        self.buffered_char = "\n"

    def run():
        '''
        while(queque not empty)
            parse #with handling errors
        '''
        pass

    def get_token(self) -> Token:
        if self.buffered_char is None:
            self.buffered_char = self.source.get_char()

        # read all of whitespaces between tokens
        while (self.buffered_char in self.WHITESPACE_ELEMENTS):
            self.buffered_char = self.source.get_char()

        if self.buffered_char in self.SINGLE_CHAR_TOKENS.keys():
            ret_val = self.buffered_char
            self.buffered_char = None
            return self.SINGLE_CHAR_TOKENS[ret_val]

        token_string = self.buffered_char
        self.buffered_char = self.source.get_char()
        token_string += self.buffered_char
        if token_string in self.TWO_CHAR_TOKENS.keys():
            self.buffered_char = None
            return self.TWO_CHAR_TOKENS[token_string]

        # Cover non-trivial single character tokens
        if token_string[0] == "<":
            return Token(TokenType.COMP_OPERATOR, "<")
        elif token_string[0] == ">":
            return Token(TokenType.COMP_OPERATOR, ">")
        elif token_string[0] == "!":
            return Token(TokenType.UNARY_OPERATOR, "!")

        if token_string[0] == '"':
            return self._parse_defined_string(token_string)

        if token_string[0] in self.LETTERS:
            return self._parse_identifier(token_string)

        if token_string[0].isdigit() and token_string[0] != "0":
            return self._parse_number(token_string)

        if token_string[0] not in self.LETTERS and not token_string[0].isdigit(
        ):
            raise UnexpectedCharacterError(
                "Unknown token, unexpected first character: " +
                token_string[0])

    def _parse_defined_string(self, token_string):

        while (self.buffered_char != '"'):
            self.buffered_char = self.source.get_char()
            token_string += self.buffered_char
        # TODO error handling and add quote escaping
        self.buffered_char = None
        return Token(TokenType.CONST, token_string)

    def _parse_identifier(self, token_string):

        while self.buffered_char in self.LETTERS + ["_"] + self.NUMBERS:
            token_string += self.buffered_char
            self.buffered_char = self.source.get_char()

        if token_string in self.RESTRICTED_IDENTIFIERS.keys():
            return self.RESTRICTED_IDENTIFIERS[token_string]

        return Token(TokenType.IDENTIFIER, token_string)

    def _parse_number(self, token_string):
        # parsing first part of number (before dot)
        while (self.buffered_char.isdigit()):
            self.buffered_char = self.source.get_char()
            if self.buffered_char.isdigit():
                token_string += self.buffered_char

        if (self.buffered_char == "."):
            token_string += self.buffered_char
            self.buffered_char = self.source.get_char()
            if not self.buffered_char.isdigit():
                raise UnexpectedCharacterError(
                    "Unexpected character while parsing number: " +
                    token_string)
            while (self.buffered_char.isdigit()):
                token_string += self.buffered_char
                self.buffered_char = self.source.get_char()

        if not token_string[-1].isdigit():
            raise UnexpectedCharacterError(
                "Not number at the end of const number: " + token_string)

        return Token(TokenType.CONST, token_string)
