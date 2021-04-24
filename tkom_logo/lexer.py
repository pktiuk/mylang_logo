from shared import ConsoleLogger, Token, TokenType, Location
from queue import Queue


class TextReader:
    """Base class for queque reading letters
    """
    def get_char(self) -> str:
        """if buffer empty then wait

        Returns:
            single character (or 0x00 when closing)
        """
        raise NotImplementedError

    def close(self):
        """Prepares Reader for closing
        get_char will return 0x00 instead of waiting for
        empty queue
        """
        raise NotImplementedError

    def get_location(self) -> Location:
        raise NotImplementedError


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
    WHITESPACE_ELEMENTS = [" ", "\t"]

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
        "\n": Token(TokenType.EOL, "\n"),
        ".": Token(TokenType.FIELD_OPERATOR, "."),
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

    def __init__(self,
                 source: TextReader,
                 logger=ConsoleLogger(),
                 output_queque: Queue = Queue(maxsize=10)):
        self.source = source
        self.logger = logger
        self.output_queque = output_queque
        self.buffered_char = None
        self.current_location = Location(0, 0)

        self.is_running = False

    def start(self):
        """Starts continously processing characters from source and putting them
        into specified queuq

        Raises:
            Exception: raised when no output Queue is defined
        """
        if self.output_queque is None:
            raise Exception("No output Queue defined")

        self.is_running = True
        while (self.is_running):
            try:
                t = self.get_token()
                self.output_queque.put(t)
                if t.symbol_type == TokenType.EOF:
                    self.is_running = False
            except UnexpectedCharacterError as exc:
                self.logger.error(str(exc))
            except UnexpectedCharacterError as exc:
                self.logger.error(str(exc))
            except Exception as exc:
                self.logger.error("Unexpected exception occured: " + str(exc))
        self.is_running = False

    def stop(self):
        self.source.close()

    def _add_loaded_location_to_token(decorated_fun, *args, **kwargs):
        def output_fun(*args, **kwargs):
            t = decorated_fun(*args, **kwargs)
            t.location = args[0].current_location
            return t

        return output_fun

    @_add_loaded_location_to_token
    def get_token(self) -> Token:
        if self.buffered_char is None:
            self._get_char()

        # read all of whitespaces between tokens
        while (self.buffered_char in self.WHITESPACE_ELEMENTS):
            self._get_char()

        if self.buffered_char == '\0':
            return Token(TokenType.EOF, "")

        self.current_location = self.source.get_location()

        if self.buffered_char in self.SINGLE_CHAR_TOKENS.keys():
            ret_val = self.buffered_char
            self.buffered_char = None
            return self.SINGLE_CHAR_TOKENS[ret_val]

        token_string = self.buffered_char
        self._get_char()
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
        elif token_string[0] == "=":
            return Token(TokenType.ASSIGNMENT_OPERATOR, "=")

        if token_string[0] == '"':
            return self._parse_defined_string(token_string)

        if token_string[0] in self.LETTERS:
            token_string = token_string[0]
            return self._parse_identifier(token_string)

        if token_string[0].isdigit():
            return self._parse_number(token_string)

        if token_string[0] not in self.LETTERS and not token_string[0].isdigit(
        ):
            raise UnexpectedCharacterError(
                f"Unknown token, unexpected first character in token: {token_string}"
            )

    def _parse_defined_string(self, token_string):

        while (self.buffered_char != '"'):
            self._get_char()
            token_string += self.buffered_char
            if token_string[-2::] == '\\"':
                self._get_char()
                token_string += self.buffered_char

        self.buffered_char = None
        return Token(TokenType.CONST, token_string)

    def _parse_identifier(self, token_string):

        while self.buffered_char in self.LETTERS + ["_"] + self.NUMBERS:
            token_string += self.buffered_char
            self._get_char()

        if token_string in self.RESTRICTED_IDENTIFIERS.keys():
            return self.RESTRICTED_IDENTIFIERS[token_string]

        return Token(TokenType.IDENTIFIER, token_string)

    def _parse_number(self, token_string):
        token_string = token_string[0]
        # parsing first part of number (before dot)
        if token_string[0] == "0":
            if self.buffered_char.isdigit():
                raise ParseError("Not allowed number format: " + token_string)
        else:
            while (self.buffered_char.isdigit()):
                token_string += self.buffered_char
                self._get_char()

        if (self.buffered_char == "."):
            token_string += self.buffered_char
            self._get_char()
            if not self.buffered_char.isdigit():
                raise ParseError("Non-digit after dot in number: " +
                                 token_string)
            while (self.buffered_char.isdigit()):
                token_string += self.buffered_char
                self._get_char()

        if not token_string[-1].isdigit():
            raise UnexpectedCharacterError(
                "Not number at the end of const number: " + token_string)
        if self.buffered_char in self.LETTERS:
            raise UnexpectedCharacterError(
                "Number shouldn't contain any letters.")

        return Token(TokenType.CONST, token_string)

    def _get_char(self):
        self.buffered_char = self.source.get_char()
        return self.buffered_char
