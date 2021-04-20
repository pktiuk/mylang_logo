from shared import ConsoleLogger, Token, TokenType, Location


class Lexer():
    def __init__(self, logger=ConsoleLogger()):
        self.source = None
        self.logger = logger
        self.output = None

    def get_token(self) -> Token:
        return None
