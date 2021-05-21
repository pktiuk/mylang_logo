from .lexer import Lexer
from .shared import Token, TokenType, ConsoleLogger, Logger
from .language_errors import SyntaxError
from .node_classes import Relation, Statement, Expression, ValueAssignment, MathExpression, Factor, Value, Relation, AndCondition, OrCondition, FieldOperator, FunOperator, IdValue, ConstValue, Block, IfStatement, WhileStatement, FunctionDefinition, Definition, Program, LogicalExpression, AddExpression


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

    def _check_token_type(self,
                          token_type: TokenType,
                          pop_if_true: bool = False) -> bool:
        result = token_type == self.__get_token().symbol_type
        if pop_if_true and result:
            self.__pop_token()
        return result

    def parse_program(self) -> Program:
        parsed = self.parse()
        if parsed:
            program = Program()
            while parsed:
                program.add_element(parsed)
                parsed = self.parse()
            return program

        return None

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
        return self.__parse_logical_expression()

    def __parse_logical_expression(self, unary_op=None):
        first_exp = self.__parse_and_condition()
        if not first_exp:
            return None

        other_exp = []
        while self._check_token_type(TokenType.OR_OPERATOR, True):
            other_exp.append(self.__parse_and_condition())

        if other_exp:
            other_exp.insert(0, first_exp)
            return LogicalExpression(other_exp, unary_op)
        else:
            return first_exp

    def __parse_and_condition(self) -> Expression:

        first_relation = self.__parse_relation()
        if not first_relation:
            return None

        other_relations = []

        while self._check_token_type(TokenType.AND_OPERATOR, True):
            other_relations.append(self.__parse_relation())

        if other_relations:
            other_relations.insert(0, first_relation)
            return AndCondition(other_relations)
        else:
            return first_relation

    def __parse_relation(self) -> Relation:
        first_math_expression = self.__parse_math_expression()

        if self._check_token_type(TokenType.COMP_OPERATOR):
            comp = self.__pop_token().value
            return Relation(first_math_expression,
                            self.__parse_math_expression(), comp)
        else:
            return first_math_expression

    def __parse_math_expression(self) -> MathExpression:
        first_add_expr = self.__parse_add_expr()

        operators = []
        add_expressions = [first_add_expr]
        while self._check_token_type(TokenType.ADD_OPERATOR):
            operators.append(self.__pop_token().value)
            add_exp = self.__parse_add_expr()
            if not add_exp:
                raise SyntaxError("No factor after add operator")
            add_expressions.append(add_exp)

        if operators:
            return MathExpression(add_expressions, operators)
        else:
            return first_add_expr

    def __parse_add_expr(self) -> AddExpression:
        first_factor = self.__parse_factor()
        operators = []
        factors = [first_factor]

        while self._check_token_type(TokenType.MULT_OPERATOR):
            operators.append(self.__pop_token().value)
            factor = self.__parse_factor()
            if not factor:
                raise SyntaxError("No factor after add operator")
            factors.append(factor)

        if operators:
            return AddExpression(factors, operators)
        else:
            return first_factor

    def __parse_factor(self) -> Factor:
        result = None

        unary_token = None
        if self.__get_token().symbol_type in [
                TokenType.UNARY_OPERATOR, TokenType.ADD_OPERATOR
        ]:
            unary_token = self.__pop_token().value

        if self._check_token_type(TokenType.OPEN_PAREN, True):
            result = self.__parse_logical_expression(unary_token)
            self.__validate_next_token(TokenType.CLOSE_PAREN,
                                       "No ending parenthesis.")
        else:
            result = self.__parse_value()
            if result and unary_token:
                result = Factor(result, unary_token)
        return result

    def __parse_value(self) -> Value:
        if self._check_token_type(TokenType.CONST):
            token = self.__pop_token()
            return ConstValue(token.location, token.value)
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
            self.__validate_next_token(TokenType.CLOSE_PAREN,
                                       "Missing close paren", False)
        self.__pop_token()
        return FunOperator(location, arguments)

    def __parse_while(self) -> WhileStatement:
        if self.__get_token().symbol_type != TokenType.WHILE:
            return None
        loc = self.__pop_token().location
        self.__validate_next_token(TokenType.OPEN_PAREN,
                                   "No opening paren after while definition")
        logical_exp = self.__parse_expression()
        self.__validate_next_token(TokenType.CLOSE_PAREN,
                                   "No closing paren after while definition")

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

        self.__validate_next_token(
            TokenType.OPEN_PAREN, "No opening paren after function definition")
        arguments = []
        # parse arguments
        if self._check_token_type(TokenType.IDENTIFIER):
            arguments.append(self.__pop_token().value)

        while self._check_token_type(TokenType.COMMA):
            self.__pop_token()
            self.__validate_next_token(TokenType.IDENTIFIER,
                                       "Wrong function argument", False)
            arguments.append(self.__pop_token().value)

        self.__validate_next_token(TokenType.CLOSE_PAREN,
                                   "Missing close paren")

        block = self.__parse_block()
        return FunctionDefinition(fun.location, fun.value, block, arguments)

    def __parse_block(self) -> Block:
        self.__validate_next_token(TokenType.OPEN_BLOCK,
                                   "No opening block in block declaration")
        statements = []
        statement = self.__parse_statement()
        while statement:
            statements.append(statement)
            statement = self.__parse_statement()

        self.__validate_next_token(TokenType.CLOSE_BLOCK, "No close of block")
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

        self.__validate_next_token(TokenType.OPEN_PAREN, "No opening paren if")

        condition = self.__parse_expression()
        self.__validate_next_token(TokenType.CLOSE_PAREN,
                                   "No closing paren after if condition")

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
        self.__validate_next_token(TokenType.IDENTIFIER,
                                   "Wrong token after dot", False)
        return FieldOperator(loc, self.__pop_token().value)

    def __validate_next_token(self,
                              expected_type: TokenType,
                              err_msg: str,
                              pop: bool = True):
        """loads token and checks whether it token matches 
           expected one and raises SyntaxError if not
        """
        if not self._check_token_type(expected_type):
            raise SyntaxError(err_msg)
        if pop:
            self.__pop_token()
