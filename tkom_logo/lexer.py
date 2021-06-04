from .shared import ConsoleLogger, Token, TokenType, Location
from .language_errors import UnexpectedCharacterError, ParseError
from .text_reader import TextReader


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
        ",":
        lambda self: Token(TokenType.COMMA, ","),
        "<":
        lambda self: Token(TokenType.COMP_OPERATOR, "<=")
        if self._get_char() == "=" else Token(TokenType.COMP_OPERATOR, "<"),
        ">":
        lambda self: Token(TokenType.COMP_OPERATOR, ">=")
        if self._get_char() == "=" else Token(TokenType.COMP_OPERATOR, ">"),
        "=":
        lambda self: Token(TokenType.COMP_OPERATOR, "==") if self._get_char(
        ) == "=" else Token(TokenType.ASSIGNMENT_OPERATOR, "="),
        "!":
        lambda self: Token(TokenType.COMP_OPERATOR, "!=")
        if self._get_char() == "=" else Token(TokenType.UNARY_OPERATOR, "!"),
        "|":
        lambda self: Token(TokenType.OR_OPERATOR, "||") if self._get_char(
        ) == "|" else Lexer._raise_error(UnexpectedCharacterError),
        "&":
        lambda self: Token(TokenType.AND_OPERATOR, "&&") if self._get_char() ==
        "&" else Lexer._raise_error(UnexpectedCharacterError),
    }

    RESTRICTED_IDENTIFIERS = {
        "fun": lambda: Token(TokenType.FUN, "fun"),
        "while": lambda: Token(TokenType.WHILE, "while"),
        "if": lambda: Token(TokenType.IF, "if"),
        "else": lambda: Token(TokenType.ELSE, "else"),
    }

    def __init__(self, source: TextReader, logger=ConsoleLogger()):
        self.source = source
        self.logger = logger
        self.buffered_char = None
        self.current_location = Location(0, 0)

        self.is_running = False

    def _handle_returned_token(decorated_fun, *args, **kwargs):
        def output_fun(*args, **kwargs):
            try:
                t = decorated_fun(*args, **kwargs)
                t.location = args[0].current_location
            except (UnexpectedCharacterError, ParseError) as err:
                err.location = args[0].current_location
                raise err
            return t

        return output_fun

    @_handle_returned_token
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
        value = float(self.buffered_char)
        # parsing first part of number (before dot)
        if self.buffered_char == "0":
            if self._get_char().isdigit():
                raise ParseError("Not allowed number format (0xx)")
        else:
            while (self._get_char().isdigit()):
                value = 10 * value + float(self.buffered_char)

        if (self.buffered_char == "."):
            if not self._get_char().isdigit():
                raise ParseError("Non-digit after dot in number")

            denominator = 10
            numerator = float(self.buffered_char)
            while (self._get_char().isdigit()):
                denominator *= 10
                numerator = numerator * 10 + float(self.buffered_char)
            value = value + numerator / denominator

        if self.buffered_char.isalpha():
            raise UnexpectedCharacterError(
                "Number shouldn't contain any letters.")

        return Token(TokenType.CONST, value)

    def _get_char(self) -> str:
        self.buffered_char = self.source.get_char()
        return self.buffered_char

    @staticmethod
    def _raise_error(error):
        raise error
