from lexer import Lexer, TextReader
from shared import Token, TokenType, ConsoleLogger, Logger, Location
from language_errors import SyntaxError
from node_classes import Statement, Expression, ValueAssignment, MathExpression, Factor, Value, Comparison, AndCondition, OrCondition, FieldOperator, FunOperator, IdValue, ConstValue, Block, IfStatement, WhileStatement, FunctionDefinition, Definition


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

    def parse(self) -> Statement:
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
            assignment = self.__parse_assignment(result)
            result = assignment if assignment else result
        return result

    def __parse_assignment(self, target: IdValue):
        if target:
            if type(target) == IdValue and self.__get_token(
            ).symbol_type == TokenType.ASSIGNMENT_OPERATOR:
                self.__pop_token()
                return ValueAssignment(target.location, target.name,
                                       self.__parse_expression())
        return None

    def __parse_definition(self) -> Definition:
        return self.__parse_function_def()

    def __parse_expression(self) -> Expression:
        if self._check_token_type(TokenType.CLOSE_PAREN):
            return None
        if self._check_token_type(TokenType.OPEN_PAREN):
            self.__pop_token()
            result = self.__parse_math_expression()
            if self.__pop_token().symbol_type != TokenType.CLOSE_PAREN:
                raise SyntaxError("No ending parenthesis.")
            return result

        result = self.__parse_math_expression()

        if result:
            logic = self.__parse_logical_expression(result)
            if logic:
                return logic

        return result

    def __parse_logical_expression(self, first_math_expression):
        logical_operators = [
            TokenType.OR_OPERATOR, TokenType.AND_OPERATOR,
            TokenType.COMP_OPERATOR
        ]
        if self.__get_token().symbol_type in logical_operators:
            result = self.__parse_and_condition(first_math_expression)
            if self._check_token_type(TokenType.OR_OPERATOR):
                self.__pop_token()
                result = OrCondition(result, self.__parse_expression())
            return result
        return None

    def __parse_and_condition(self, first_math_expression) -> AndCondition:

        result = self.__parse_relation(first_math_expression)
        if not result:
            raise SyntaxError("")

        if self._check_token_type(TokenType.AND_OPERATOR):
            self.__pop_token()
            first_math_expression = self.__parse_math_expression()
            if not first_math_expression:
                raise SyntaxError("")

            return AndCondition(
                result, self.__parse_and_condition(first_math_expression))

        return result

    def __parse_relation(self, first_math_expression) -> Comparison:

        if not first_math_expression:
            first_math_expression = self.__parse_math_expression()

        if self._check_token_type(TokenType.COMP_OPERATOR):
            comp = self.__pop_token().value
            return Comparison(first_math_expression,
                              self.__parse_math_expression(), comp)
        else:
            return None

    def __parse_math_expression(self) -> Expression:
        result = self.__parse_factor()

        if self._check_token_type(TokenType.ADD_OPERATOR):
            operator = self.__pop_token().value
            result = MathExpression(result, self.__parse_math_expression(),
                                    operator)
        return result

    def __parse_factor(self) -> Factor:
        result = None
        if self._check_token_type(TokenType.OPEN_PAREN):
            self.__pop_token()
            result = self.__parse_math_expression()
            if not self._check_token_type(TokenType.CLOSE_PAREN):
                raise SyntaxError("No ending parenthesis.")
            self.__pop_token()
        else:
            result = self.__parse_value()
            if self._check_token_type(TokenType.MULT_OPERATOR):
                mult_op = self.__pop_token().value
                result = Factor(result.location, result, self.__parse_factor(),
                                mult_op)

        return result

    def __parse_value(self) -> Value:
        if self._check_token_type(TokenType.CONST):
            token = self.__pop_token()
            return ConstValue(token.location, token.value)
        elif self.__get_token().symbol_type in [
                TokenType.UNARY_OPERATOR, TokenType.ADD_OPERATOR
        ]:
            unary_token = self.__pop_token()
            if self.__get_token().symbol_type in [
                    TokenType.IDENTIFIER, TokenType.CONST
            ]:
                token = self.__pop_token()
                return ConstValue(token.location, token.value,
                                  unary_token.value)
            raise SyntaxError(
                f'Wrong token ({self.__get_token()}) after unary operation ')

        elif self._check_token_type(TokenType.IDENTIFIER):
            id_token = self.__pop_token()
            operators = []

            operator = True
            while operator:
                operator = self.__parse_function_operator()
                if not operator:
                    operator = self.__parse_field_operator()
                if operator:
                    operators.append(operator)
            return IdValue(id_token.location,
                           id_token.value,
                           operators=operators)

        return None

    def __parse_function_operator(self) -> FunOperator:
        if not self._check_token_type(TokenType.OPEN_PAREN):
            return None
        location = self.__pop_token().location

        # Parsing arguments

        argument = self.__parse_expression()
        arguments = []
        if argument:
            arguments = [argument]
            while self._check_token_type(TokenType.COMMA):
                self.__pop_token()
                argument = self.__parse_expression()
                if argument:
                    arguments.append(argument)
                else:
                    raise SyntaxError("Problem with parsing arguments")
            if not self._check_token_type(TokenType.CLOSE_PAREN):
                raise SyntaxError("Missing close paren")
        self.__pop_token()
        return FunOperator(location, arguments)

    def __parse_while(self) -> WhileStatement:
        if not self._check_token_type(TokenType.WHILE):
            return None
        loc = self.__pop_token().location
        if not self._check_token_type(TokenType.OPEN_PAREN):
            raise SyntaxError("No opening paren after while definition")
        self.__pop_token()
        logical_exp = self.__parse_expression()
        if not self._check_token_type(TokenType.CLOSE_PAREN):
            raise SyntaxError("No closing paren after while definition")
        self.__pop_token()

        block = self.__parse_block()
        return WhileStatement(loc, logical_exp, block)

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

        if not self._check_token_type(TokenType.OPEN_PAREN):
            raise SyntaxError("No opening paren after function definition")
        self.__pop_token()
        arguments = []
        # parse arguments
        if self._check_token_type(TokenType.IDENTIFIER):
            arguments.append(self.__pop_token().value)

        while self._check_token_type(TokenType.COMMA):
            self.__pop_token()
            if not self._check_token_type(TokenType.IDENTIFIER):
                raise SyntaxError("Wrong function argument")
            arguments.append(self.__pop_token().value)

        if not self._check_token_type(TokenType.CLOSE_PAREN):
            raise SyntaxError("Missing close paren")
        self.__pop_token()

        block = self.__parse_block()
        return FunctionDefinition(fun.location, fun.value, block, arguments)

    def __parse_block(self) -> Block:
        if not self._check_token_type(TokenType.OPEN_BLOCK):
            raise SyntaxError("No opening block in block declaration")
        self.__pop_token()
        statements = []
        statement = self.__parse_statement()
        while statement:
            statements.append(statement)
            statement = self.__parse_statement()

        if not self._check_token_type(TokenType.CLOSE_BLOCK):
            raise SyntaxError("No close of block")
        self.__pop_token()
        return Block(statements)

    def __parse_if(self) -> IfStatement:
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

    def __parse_field_operator(self) -> FieldOperator:
        if not self._check_token_type(TokenType.FIELD_OPERATOR):
            return None
        loc = self.__pop_token().location
        if not self._check_token_type(TokenType.IDENTIFIER):
            raise SyntaxError("Wrong token after dot")
        return FieldOperator(loc, self.__pop_token().value)
