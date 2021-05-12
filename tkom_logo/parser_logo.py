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
        if self.current_token:
            res = self.current_token
            self.current_token = None
            return res
        else:
            return self.token_source.get()

    def _check_token_type(self, token_type: TokenType) -> bool:
        return token_type == self._get_token().symbol_type

    def parse(self) -> ParserNode:
        while self._check_token_type(TokenType.EOL):
            self._pop_token()
        result = self.parse_statement()
        return result

    def parse_statement(self) -> ParserNode:

        if self._check_token_type(TokenType.FUN):
            return self.parse_function_def()
        elif self._check_token_type(TokenType.WHILE):
            return self.parse_while()
        elif self._check_token_type(TokenType.IF):
            return self.parse_if()
        else:
            result = self.parse_expression()

            # check if assignment
            if result.children == [] and self._get_token(
            ).symbol_type == TokenType.ASSIGNMENT_OPERATOR:
                return ParserNode(self._pop_token(),
                                  [result, self.parse_expression()])
            else:
                return result

    def parse_expression(self) -> ParserNode:
        if self._check_token_type(TokenType.OPEN_PAREN):
            self._pop_token()
            result = self.parse_math_expression()
            if self._pop_token().symbol_type != TokenType.CLOSE_PAREN:
                raise SyntaxError("No ending parenthesis.")
            return result

        result = self.parse_math_expression()
        logical_operators = [
            TokenType.OR_OPERATOR, TokenType.AND_OPERATOR,
            TokenType.COMP_OPERATOR
        ]
        if self._get_token().symbol_type in logical_operators:
            result = self.parse_and_condition(result)
            while self._check_token_type(TokenType.OR_OPERATOR):
                result = ParserNode(
                    self._pop_token(),
                    [result, self.parse_and_condition()])

        return result

    def parse_and_condition(self, first_math_expression) -> ParserNode:
        result = None
        if self._check_token_type(TokenType.COMP_OPERATOR):
            result = ParserNode(
                self._pop_token(),
                [first_math_expression,
                 self.parse_math_expression()])
            first_math_expression = None

        while self._check_token_type(TokenType.AND_OPERATOR):
            and_operator = self._pop_token()
            relation = self.parse_relation(first_math_expression)
            first_math_expression = None
            if result:
                result = ParserNode(and_operator, [result, relation])
            else:
                result = relation
        return result

    def parse_relation(self, first_math_expression=None) -> ParserNode:
        if not first_math_expression:
            first_math_expression = self.parse_math_expression()

        if self._check_token_type(TokenType.COMP_OPERATOR):
            return ParserNode(
                self._pop_token(),
                [first_math_expression,
                 self.parse_math_expression()])
        else:
            return first_math_expression

    def parse_math_expression(self) -> ParserNode:
        result = self.parse_factor()
        while self._check_token_type(TokenType.MULT_OPERATOR):
            mult_token = self._pop_token()
            new_tree = self.parse_factor()
            result = ParserNode(token=mult_token, children=[result, new_tree])

        if self._check_token_type(TokenType.ADD_OPERATOR):
            result = ParserNode(
                self._pop_token(),
                children=[result, self.parse_math_expression()])
        return result

    def parse_factor(self) -> ParserNode:
        result = None
        if self._check_token_type(TokenType.OPEN_PAREN):
            self._pop_token()
            result = self.parse_math_expression()
            if not self._check_token_type(TokenType.CLOSE_PAREN):
                raise SyntaxError("No ending parenthesis.")
            self._pop_token()
        else:
            result = self.parse_value()
        return result

    def parse_value(self) -> ParserNode:
        if self._check_token_type(TokenType.CONST):
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
                f'Wrong token ({self._get_token()}) after unary operation ')
        elif self._check_token_type(TokenType.IDENTIFIER):
            result = ParserNode(self._pop_token())
            while self._check_token_type(TokenType.OPEN_PAREN):
                result = self.parse_function_operator(result)
            return result

        raise RuntimeError()

    def parse_function_operator(self, function: ParserNode) -> ParserNode:
        fun_operator = self._pop_token()
        fun_operator.symbol_type = TokenType.FUN_OPERATOR
        result = ParserNode(fun_operator, [function])
        # Parsing arguments
        if not self._check_token_type(TokenType.CLOSE_PAREN):
            result.children.append(self.parse_expression())
        while not self._check_token_type(TokenType.CLOSE_PAREN):
            if not self._check_token_type(TokenType.COMMA):
                raise SyntaxError(
                    "No comma or close parenthesis after argument expression")
            self._pop_token()
            result.children.append(self.parse_expression())
        self._pop_token()
        return result

    def parse_while(self) -> ParserNode:
        loop = ParserNode(self._pop_token())
        if not self._check_token_type(TokenType.OPEN_PAREN):
            raise SyntaxError("No opening paren after while definition")
        self._pop_token()
        logical_exp = self.parse_expression()
        if not self._check_token_type(TokenType.CLOSE_PAREN):
            raise SyntaxError("No closing paren after while definition")
        self._pop_token()
        loop.children.append(logical_exp)
        loop.children.append(self.parse_block())
        return loop

    def parse_function_def(self) -> ParserNode:
        '''
        function tree:
        fun_definition:
            - arg1
            - arg2
            ...
            - argn
            - block
        '''
        self._pop_token()
        fun = self._pop_token()
        fun.symbol_type = TokenType.FUN
        result = ParserNode(fun)
        if not self._check_token_type(TokenType.OPEN_PAREN):
            raise SyntaxError("No opening paren after function definition")
        self._pop_token()

        # parse arguments
        if self._check_token_type(TokenType.IDENTIFIER):
            result.children.append(ParserNode(self._pop_token()))

        while not self._check_token_type(TokenType.CLOSE_PAREN):
            if not self._check_token_type(TokenType.COMMA):
                raise SyntaxError("No comma between arguments")
            self._pop_token()
            if not self._check_token_type(TokenType.IDENTIFIER):
                raise SyntaxError("Wrong function argument")
            result.children.append(ParserNode(self._pop_token()))
        self._pop_token()

        block = self.parse_block()
        result.children.append(block)
        return result

    def parse_block(self) -> ParserNode:
        if not self._check_token_type(TokenType.OPEN_BLOCK):
            raise SyntaxError("No opening block in block declaration")

        result = ParserNode(self._pop_token())
        while not self._check_token_type(TokenType.CLOSE_BLOCK):
            result.children.append(self.parse_statement())
        self._pop_token()
        return result

    def parse_if(self):
        """if tree:
            IF:
            - condition
            - block
            - (optional) ELSE
            - (optional) else-block
        """
        result = ParserNode(self._pop_token())

        if not self._check_token_type(TokenType.OPEN_PAREN):
            raise SyntaxError("No opening paren if")
        self._pop_token()
        result.children.append(self.parse_expression())
        if not self._check_token_type(TokenType.CLOSE_PAREN):
            raise SyntaxError("No closing paren after if condition")
        self._pop_token()
        result.children.append(self.parse_block())

        if self._check_token_type(TokenType.ELSE):
            result.children.append(ParserNode(self._pop_token()))
            result.children.append(self.parse_block())

        return result
