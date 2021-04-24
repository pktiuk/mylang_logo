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

    # One or two-character tokens
    SHORT_TOKENS = {
        "+":
        lambda self: Token(TokenType.ADD_OPERATOR, "+"),
        "-":
        lambda self: Token(TokenType.ADD_OPERATOR, "-"),
        "*":
        lambda self: Token(TokenType.MULT_OPERATOR, "*"),
        "/":
        lambda self: Token(TokenType.MULT_OPERATOR, "/"),
        "{":
        lambda self: Token(TokenType.OPEN_BLOCK, "{"),
        "}":
        lambda self: Token(TokenType.CLOSE_BLOCK, "}"),
        "(":
        lambda self: Token(TokenType.OPEN_PAREN, "("),
        ")":
        lambda self: Token(TokenType.CLOSE_PAREN, ")"),
        ".":
        lambda self: Token(TokenType.FIELD_OPERATOR, "."),
        "<":
        lambda self: Token(TokenType.COMP_OPERATOR, "<=")
        if self._get_char() == "=" else Token(TokenType.COMP_OPERATOR, "<"),
        ">":
        lambda self: Token(TokenType.COMP_OPERATOR, ">=")
        if self._get_char() == "=" else Token(TokenType.COMP_OPERATOR, ">"),
        "=":
        lambda self: Token(TokenType.COMP_OPERATOR, "==") if self._get_char()
        == "=" else Token(TokenType.ASSIGNMENT_OPERATOR, "="),
        "!":
        lambda self: Token(TokenType.COMP_OPERATOR, "!=")
        if self._get_char() == "=" else Token(TokenType.UNARY_OPERATOR, "!"),
        "|":
        lambda self: Token(TokenType.OR_OPERATOR, "||")
        if self._get_char() == "" else UnexpectedCharacterError,
        "&":
        lambda self: Token(TokenType.AND_OPERATOR, "&&")
        if self._get_char() == "" else UnexpectedCharacterError,
    }  # TODO properly raise errors from above

    RESTRICTED_IDENTIFIERS = {
        "fun": lambda: Token(TokenType.FUN, "fun"),
        "while": lambda: Token(TokenType.WHILE, "while"),
        "if": lambda: Token(TokenType.IF, "if"),
        "else": lambda: Token(TokenType.ELSE, "else"),
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
        if self.buffered_char.isspace():
            while (self._get_char().isspace()):
                pass

        if self.buffered_char == '\0':
            return Token(TokenType.EOF, "")

        self.current_location = self.source.get_location()

        generator = self.SHORT_TOKENS.get(self.buffered_char)

        if generator:
            token = generator(self)
            if token.value[-1] == self.buffered_char:
                self.buffered_char = None
            return token

        if self.buffered_char == '"':
            return self._parse_defined_string()

        if self.buffered_char.isalpha():
            return self._parse_identifier()

        if self.buffered_char.isdigit():
            return self._parse_number()

        if not self.buffered_char.isalpha() and not self.buffered_char.isdigit(
        ):
            raise UnexpectedCharacterError(
                f"Unknown token, unexpected first character: {self.buffered_char}"
            )

    def _parse_defined_string(self):
        token_string = self.buffered_char
        while (self._get_char() != '"'):
            if self.buffered_char == "\0":
                raise EOFError(
                    f'Unexpected EOF during string parse: {token_string}')
            token_string += self.buffered_char
            if token_string[-1] == '\\':
                self._get_char()
                token_string += self.buffered_char
        token_string += self.buffered_char
        self.buffered_char = None

        return Token(TokenType.CONST, token_string)

    def _parse_identifier(self):
        token_string = ""
        while self.buffered_char.isalnum() or self.buffered_char == "_":
            token_string += self.buffered_char
            self._get_char()

        generator = self.RESTRICTED_IDENTIFIERS.get(token_string)
        if generator:
            return generator()

        return Token(TokenType.IDENTIFIER, token_string)

    def _parse_number(self):
        token_string = self.buffered_char
        # parsing first part of number (before dot)
        if self.buffered_char == "0":
            if self._get_char().isdigit():
                raise ParseError("Not allowed number format: " + token_string)
        else:
            while (self._get_char().isdigit()):
                token_string += self.buffered_char

        if (self.buffered_char == "."):
            token_string += self.buffered_char

            if not self._get_char().isdigit():
                raise ParseError("Non-digit after dot in number: " +
                                 token_string)

            token_string += self.buffered_char
            while (self._get_char().isdigit()):
                token_string += self.buffered_char

        if not token_string[-1].isdigit():
            raise UnexpectedCharacterError(
                "Not number at the end of const number: " + token_string)
        if self.buffered_char.isalpha():
            raise UnexpectedCharacterError(
                "Number shouldn't contain any letters.")

        return Token(TokenType.CONST, token_string)

    def _get_char(self) -> str:
        self.buffered_char = self.source.get_char()
        return self.buffered_char
