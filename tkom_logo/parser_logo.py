from lexer import Lexer, TextReader
from shared import ParserNode, Token, TokenType, ConsoleLogger, Logger, Location
from language_errors import SyntaxError


class Program(object):
    def __init__(self):
        self.definitions_list = []
        self.statements = []


class Statement(object):
    def __init__(self, loc: Location):
        self.location = loc


class Expression(Statement):
    def __init__(self, loc: Location):
        super().__init__(loc)

    def get_value(self):
        raise NotImplementedError


class MathExpression(Expression):
    def __init__(self, loc: Location):
        super().__init__(loc)
        self.products = []


class Factor(MathExpression):
    def __init__(self, loc: Location):
        super().__init__(loc)
        self.elements = []


class Value(Factor):
    def __init__(self, loc: Location):
        super().__init__(loc)


class ConstValue(Value):
    def __init__(self, loc: Location, value, unary_op=None):
        super().__init__(loc)
        self.value = value
        self.unary_op = unary_op


class LogicalExpression(Expression):
    def __init__(self, loc: Location):
        super().__init__(loc)


class Block(object):
    def __init__(self):
        self.definitions_list = []
        self.statements = []


class IfStatement(Statement):
    def __init__(self,
                 loc: Location,
                 condition: LogicalExpression,
                 true_block: Block,
                 false_block: Block = None):
        super().__init__(loc)
        self.condition = condition
        self.true_block = true_block
        self.false_block = false_block

    def __str__(self, depth=0):
        ret = "\t" * depth + "IF\n"
        ret += self.condition.__str__(depth + 1)
        ret += self.true_block.__str__(depth + 1)
        if self.false_block:
            ret += self.false_block.__str__(depth + 1)
        else:
            ret += "None else"
        return ret


class Definition(object):
    def __init__(self, loc: Location):
        self.location = loc


class FunctionDefinition(Definition):
    def __init__(self, loc: Location, condition: LogicalExpression,
                 block: Block):
        super().__init__(loc)
        self.condition = condition
        self.block = block


class Parser(object):
    def __init__(self,
                 token_source: Lexer = None,
                 logger: Logger = ConsoleLogger):
        self.current_token = None
        self.token_source = token_source

    def __get_token(self) -> Token:
        if not self.current_token:
            self.current_token = self.token_source.get_token()
        return self.current_token

    def __pop_token(self):
        if self.current_token:
            res = self.current_token
            self.current_token = None
            return res
        else:
            return self.token_source.get_token()

    def _check_token_type(self, token_type: TokenType) -> bool:
        return token_type == self.__get_token().symbol_type

    def parse(self) -> ParserNode:
        try:
            result = self.__parse_definition()
            if result:
                return result
            return self.__parse_statement()
        except SyntaxError as err:
            err.location = self.__get_token().location
            raise err

    def __parse_statement(self) -> Statement:

        result = self.__parse_while()
        if result:
            return result
        result = self.__parse_if()
        if result:
            return result

        result = self.__parse_expression()
        if result:
            # check if assignment
            if result.children == [] and self.__get_token(
            ).symbol_type == TokenType.ASSIGNMENT_OPERATOR:
                return ParserNode(self.__pop_token(),
                                  [result, self.__parse_expression()])
        return result

    def __parse_definition(self) -> Definition:
        return self.__parse_function_def()

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

    def __parse_and_condition(self, first_math_expression=None) -> ParserNode:
        if not first_math_expression:
            first_math_expression = self.__parse_math_expression()
        result = first_math_expression
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
        if not self._check_token_type(TokenType.WHILE):
            return None
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

    def __parse_function_def(self) -> FunctionDefinition:
        '''
        function tree:
        fun_definition:
            - arg1
            - arg2
            ...
            - argn
            - block
        '''
        if not self._check_token_type(TokenType.FUN):
            return None
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
        if not self._check_token_type(TokenType.IF):
            return None
        location = self.__pop_token().location

        if not self._check_token_type(TokenType.OPEN_PAREN):
            raise SyntaxError("No opening paren if")
        self.__pop_token()

        condition = self.__parse_expression()
        if not self._check_token_type(TokenType.CLOSE_PAREN):
            raise SyntaxError("No closing paren after if condition")
        self.__pop_token()

        true_block = self.__parse_block()
        result = IfStatement(location,
                             condition=condition,
                             true_block=true_block)

        if self._check_token_type(TokenType.ELSE):
            self.__pop_token()
            result.false_block = self.__parse_block()

        return result

    def __parse_field_operator(self, source: ParserNode) -> ParserNode:
        result = ParserNode(self.__pop_token(), [source])
        if not self._check_token_type(TokenType.IDENTIFIER):
            raise SyntaxError("Wrong token after dot")
        result.children.append(ParserNode(self.__pop_token()))
        return result
