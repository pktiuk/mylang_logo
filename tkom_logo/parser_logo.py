from queue import Queue
from shared import ParserNode, Token, TokenType, ConsoleLogger, Logger
from language_errors import SyntaxError


class Parser(object):
    def __init__(self,
                 token_source: Queue = None,
                 logger: Logger = ConsoleLogger):
        self.current_token = None
        self.token_source = token_source

    def __get_token(self) -> Token:
        if not self.current_token:
            self.current_token = self.token_source.get()
        return self.current_token

    def __pop_token(self):
        if self.current_token:
            res = self.current_token
            self.current_token = None
            return res
        else:
            return self.token_source.get()

    def _check_token_type(self, token_type: TokenType) -> bool:
        return token_type == self.__get_token().symbol_type

    def parse(self) -> ParserNode:
        while self._check_token_type(TokenType.EOL):
            self.__pop_token()
        result = self.__parse_statement()
        return result

    def __parse_statement(self) -> ParserNode:

        if self._check_token_type(TokenType.FUN):
            return self.__parse_function_def()
        elif self._check_token_type(TokenType.WHILE):
            return self.__parse_while()
        elif self._check_token_type(TokenType.IF):
            return self.__parse_if()
        else:
            result = self.__parse_expression()

            # check if assignment
            if result.children == [] and self.__get_token(
            ).symbol_type == TokenType.ASSIGNMENT_OPERATOR:
                return ParserNode(self.__pop_token(),
                                  [result, self.__parse_expression()])
            else:
                return result

    def __parse_expression(self) -> ParserNode:
        if self._check_token_type(TokenType.OPEN_PAREN):
            self.__pop_token()
            result = self.__parse_math_expression()
            if self.__pop_token().symbol_type != TokenType.CLOSE_PAREN:
                raise SyntaxError("No ending parenthesis.")
            return result

        result = self.__parse_math_expression()
        logical_operators = [
            TokenType.OR_OPERATOR, TokenType.AND_OPERATOR,
            TokenType.COMP_OPERATOR
        ]
        if self.__get_token().symbol_type in logical_operators:
            result = self.__parse_and_condition(result)
            while self._check_token_type(TokenType.OR_OPERATOR):
                result = ParserNode(
                    self.__pop_token(),
                    [result, self.__parse_and_condition()])

        return result

    def __parse_and_condition(self, first_math_expression) -> ParserNode:
        result = None
        if self._check_token_type(TokenType.COMP_OPERATOR):
            result = ParserNode(
                self.__pop_token(),
                [first_math_expression,
                 self.__parse_math_expression()])
            first_math_expression = None

        while self._check_token_type(TokenType.AND_OPERATOR):
            and_operator = self.__pop_token()
            relation = self.__parse_relation(first_math_expression)
            first_math_expression = None
            if result:
                result = ParserNode(and_operator, [result, relation])
            else:
                result = relation
        return result

    def __parse_relation(self, first_math_expression=None) -> ParserNode:
        if not first_math_expression:
            first_math_expression = self.__parse_math_expression()

        if self._check_token_type(TokenType.COMP_OPERATOR):
            return ParserNode(
                self.__pop_token(),
                [first_math_expression,
                 self.__parse_math_expression()])
        else:
            return first_math_expression

    def __parse_math_expression(self) -> ParserNode:
        result = self.__parse_factor()
        while self._check_token_type(TokenType.MULT_OPERATOR):
            mult_token = self.__pop_token()
            new_tree = self.__parse_factor()
            result = ParserNode(token=mult_token, children=[result, new_tree])

        if self._check_token_type(TokenType.ADD_OPERATOR):
            result = ParserNode(
                self.__pop_token(),
                children=[result, self.__parse_math_expression()])
        return result

    def __parse_factor(self) -> ParserNode:
        result = None
        if self._check_token_type(TokenType.OPEN_PAREN):
            self.__pop_token()
            result = self.__parse_math_expression()
            if not self._check_token_type(TokenType.CLOSE_PAREN):
                raise SyntaxError("No ending parenthesis.")
            self.__pop_token()
        else:
            result = self.__parse_value()
        return result

    def __parse_value(self) -> ParserNode:
        if self._check_token_type(TokenType.CONST):
            return ParserNode(self.__pop_token())
        elif self.__get_token().symbol_type in [
                TokenType.UNARY_OPERATOR, TokenType.ADD_OPERATOR
        ]:
            unary_token = self.__pop_token()
            if self.__get_token().symbol_type in [
                    TokenType.IDENTIFIER, TokenType.CONST
            ]:
                return ParserNode(unary_token, [self.__parse_value()])

            raise SyntaxError(
                f'Wrong token ({self.__get_token()}) after unary operation ')
        elif self._check_token_type(TokenType.IDENTIFIER):
            result = ParserNode(self.__pop_token())
            while self._check_token_type(
                    TokenType.OPEN_PAREN) or self._check_token_type(
                        TokenType.FIELD_OPERATOR):
                if self._check_token_type(TokenType.OPEN_PAREN):
                    result = self.__parse_function_operator(result)
                else:
                    result = self.__parse_field_operator(result)
            return result

        raise RuntimeError()

    def __parse_function_operator(self, function: ParserNode) -> ParserNode:
        fun_operator = self.__pop_token()
        fun_operator.symbol_type = TokenType.FUN_OPERATOR
        result = ParserNode(fun_operator, [function])
        # Parsing arguments
        if not self._check_token_type(TokenType.CLOSE_PAREN):
            result.children.append(self.__parse_expression())
        while not self._check_token_type(TokenType.CLOSE_PAREN):
            if not self._check_token_type(TokenType.COMMA):
                raise SyntaxError(
                    "No comma or close parenthesis after argument expression")
            self.__pop_token()
            result.children.append(self.__parse_expression())
        self.__pop_token()
        return result

    def __parse_while(self) -> ParserNode:
        loop = ParserNode(self.__pop_token())
        if not self._check_token_type(TokenType.OPEN_PAREN):
            raise SyntaxError("No opening paren after while definition")
        self.__pop_token()
        logical_exp = self.__parse_expression()
        if not self._check_token_type(TokenType.CLOSE_PAREN):
            raise SyntaxError("No closing paren after while definition")
        self.__pop_token()
        loop.children.append(logical_exp)
        loop.children.append(self.__parse_block())
        return loop

    def __parse_function_def(self) -> ParserNode:
        '''
        function tree:
        fun_definition:
            - arg1
            - arg2
            ...
            - argn
            - block
        '''
        self.__pop_token()
        fun = self.__pop_token()
        fun.symbol_type = TokenType.FUN
        result = ParserNode(fun)
        if not self._check_token_type(TokenType.OPEN_PAREN):
            raise SyntaxError("No opening paren after function definition")
        self.__pop_token()

        # parse arguments
        if self._check_token_type(TokenType.IDENTIFIER):
            result.children.append(ParserNode(self.__pop_token()))

        while not self._check_token_type(TokenType.CLOSE_PAREN):
            if not self._check_token_type(TokenType.COMMA):
                raise SyntaxError("No comma between arguments")
            self.__pop_token()
            if not self._check_token_type(TokenType.IDENTIFIER):
                raise SyntaxError("Wrong function argument")
            result.children.append(ParserNode(self.__pop_token()))
        self.__pop_token()

        block = self.__parse_block()
        result.children.append(block)
        return result

    def __parse_block(self) -> ParserNode:
        if not self._check_token_type(TokenType.OPEN_BLOCK):
            raise SyntaxError("No opening block in block declaration")

        result = ParserNode(self.__pop_token())
        while not self._check_token_type(TokenType.CLOSE_BLOCK):
            result.children.append(self.__parse_statement())
        self.__pop_token()
        return result

    def __parse_if(self):
        """if tree:
            IF:
            - condition
            - block
            - (optional) ELSE
            - (optional) else-block
        """
        result = ParserNode(self.__pop_token())

        if not self._check_token_type(TokenType.OPEN_PAREN):
            raise SyntaxError("No opening paren if")
        self.__pop_token()
        result.children.append(self.__parse_expression())
        if not self._check_token_type(TokenType.CLOSE_PAREN):
            raise SyntaxError("No closing paren after if condition")
        self.__pop_token()
        result.children.append(self.__parse_block())

        if self._check_token_type(TokenType.ELSE):
            result.children.append(ParserNode(self.__pop_token()))
            result.children.append(self.__parse_block())

        return result

    def __parse_field_operator(self, source: ParserNode) -> ParserNode:
        result = ParserNode(self.__pop_token(), [source])
        if not self._check_token_type(TokenType.IDENTIFIER):
            raise SyntaxError("Wrong token after dot")
        result.children.append(ParserNode(self.__pop_token()))
        return result
