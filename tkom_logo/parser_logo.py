from queue import Queue
from shared import ParserNode, Token, TokenType, ConsoleLogger, Logger
from language_errors import SyntaxError


class Parser(object):
    def __init__(self,
                 token_source: Queue = None,
                 logger: Logger = ConsoleLogger):
        self.current_token = None
        self.token_source = token_source

    def _get_token(self) -> Token:
        if not self.current_token:
            self.current_token = self.token_source.get()
        return self.current_token

    def _pop_token(self):
        res = self.current_token
        self.current_token = None
        return res

    def parse(self) -> ParserNode:
        result = self.parse_statement()
        return result

    def parse_statement(self) -> ParserNode:
        result = self.parse_expression()
        return result

    def parse_expression(self) -> ParserNode:
        result = self.parse_math_expression()
        return result

    def parse_math_expression(self) -> ParserNode:
        result = self.parse_factor()
        while self._get_token().symbol_type == TokenType.MULT_OPERATOR:
            mult_token = self._pop_token()
            new_tree = self.parse_factor()
            result = ParserNode(token=mult_token, children=[result, new_tree])

        if self._get_token().symbol_type == TokenType.ADD_OPERATOR:
            result = ParserNode(
                self._pop_token(),
                children=[result, self.parse_math_expression()])
        return result

    def parse_factor(self) -> ParserNode:
        result = None
        if self._get_token().symbol_type == TokenType.OPEN_PAREN:
            self._pop_token()
            result = self.parse_math_expression()
            if self._get_token().symbol_type != TokenType.CLOSE_PAREN:
                raise SyntaxError("No ending parenthese.")
            self._pop_token()
        else:
            result = self.parse_value()
        return result

    def parse_value(self) -> ParserNode:
        if self._get_token().symbol_type == TokenType.CONST:
            return ParserNode(self._pop_token())
        elif self._get_token().symbol_type in [
                TokenType.UNARY_OPERATOR, TokenType.ADD_OPERATOR
        ]:
            unary_token = self._pop_token()
            if self._get_token().symbol_type in [
                    TokenType.IDENTIFIER, TokenType.CONST
            ]:
                return ParserNode(unary_token, [self.parse_value()])

            raise SyntaxError(
                f'Wrong token ({self.get_token()}) after unary operation ')

        raise NotImplementedError()
