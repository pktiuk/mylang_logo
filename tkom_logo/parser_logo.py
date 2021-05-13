from lexer import Lexer, TextReader
from shared import Token, TokenType, ConsoleLogger, Logger, Location
from language_errors import SyntaxError


class Program(object):
    def __init__(self):
        self.definitions_list = []
        self.statements = []


class Node(object):
    def __init__(self, loc: Location):
        self.location = loc


class Statement(Node):
    def __init__(self, loc: Location):
        super().__init__(loc)


class Expression(Statement):
    def __init__(self, loc: Location):
        super().__init__(loc)

    def get_value(self):
        raise NotImplementedError


class ValueAssignment(Statement):
    def __init__(self, loc, name, expression: Expression):
        super().__init__(loc)
        self.name = name
        self.expression = expression

    def __str__(self, depth=0):
        return depth * "\t" + self.name + self.expression.__str__(depth + 1)


class MathExpression(Expression):
    def __init__(self, left: 'Factor', right: 'MathExpression', operator: str):
        super().__init__(left.location)
        self.left = left
        self.right = right
        self.operator = operator

    def __str__(self, depth=0):
        res = "\t" * depth + self.operator + "\n"
        res += self.left.__str__(depth + 1)
        res += self.right.__str__(depth + 1)
        return res


class Factor(Expression):
    def __init__(self, loc: Location, left: 'Value', right: 'Factor',
                 operator: str):
        super().__init__(left.location)
        self.left = left
        self.right = right
        self.mult_operator = operator

    def __str__(self, depth=0):
        res = "\t" * depth + self.mult_operator + "\n"
        res += self.left.__str__(depth + 1)
        res += self.right.__str__(depth + 1)
        return res


class Value(Expression):
    def __init__(self, loc: Location):
        super().__init__(loc)


class Comparison(Expression):
    def __init__(self, left: Expression, right: Expression, comp_sign):
        super().__init__(left.location)
        self.left = left
        self.right = right
        self.comp_sign = comp_sign

    def __str__(self, depth=0):
        return ""


class AndCondition(Expression):
    def __init__(self, left: Comparison, right: 'AndCondition'):
        super().__init__(left.location)
        self.left = left
        self.right = right

    def __str__(self, depth=0):
        return ""


class OrCondition(Expression):
    def __init__(self, left: AndCondition, right: 'OrCondition'):
        super().__init__(left.location)
        self.left = left
        self.right = right

    def __str__(self, depth=0):
        return ""


class FieldOperator(Node):
    def __init__(self, loc: Location, name):
        super().__init__(loc)
        self.name = name

    def __str__(self, depth=0):
        return "\t" * depth + f". {self.name}"


class FunOperator(Node):
    def __init__(self, loc: Location, arguments):
        super().__init__(loc)
        self.arguments = arguments

    def __str__(self, depth=0):
        ret = "\t" * depth + f"()"
        for arg in self.arguments:
            ret += arg.__str__(depth + 1)
        return ret


class IdValue(Value):
    def __init__(self,
                 loc: Location,
                 name: str,
                 unary_op=None,
                 operators=None):
        super().__init__(loc)
        self.name = name
        self.unary_op = unary_op
        if operators:
            self.operators = operators
        else:
            self.operators = []

    def __str__(self, depth=0):
        res = ""
        for op in reversed(self.operators):
            res += op.__str__(depth)
            depth = depth + 1
        res += "\t" * depth + self.name + "\n"
        return res


class ConstValue(Value):
    def __init__(self, loc: Location, value, unary_op=None):
        super().__init__(loc)
        self.value = value
        self.unary_op = unary_op

    def __str__(self, depth=0):
        return "\t" * depth + str(self.value) + "\n"

    def get_value(self):
        if not self.unary_op:
            return self.value
        else:
            raise NotImplementedError


class LogicalExpression(Expression):
    def __init__(self, loc: Location):
        super().__init__(loc)


class Block(object):
    def __init__(self, statements: list):
        self.statements = statements

    def __str__(self, depth=0):
        res = depth * "\t" + "BLOCK\n"
        for statement in self.statements:
            res += statement.__str__(depth + 1)
        return res


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


class WhileStatement(Statement):
    def __init__(self, loc: Location, condition: LogicalExpression,
                 block: Block):
        super().__init__(loc)
        self.condition = condition
        self.block = block

    def __str__(self, depth=0):
        ret = "\t" * depth + "While cond:"
        ret += self.condition.__str__(depth + 1)
        ret += self.block.__str__(depth + 1)
        return ret


class Definition(object):
    def __init__(self, loc: Location, name: str):
        self.location = loc
        self.name = name


class FunctionDefinition(Definition):
    def __init__(
        self,
        loc: Location,
        name: str,
        block: Block,
        arguments: list = None,
    ):
        super().__init__(loc, name)
        if arguments:
            self.arguments = arguments
        else:
            self.arguments = []
        self.block = block

    def __str__(self, depth=0):
        ret = "\t" * depth + f"FUN: {self.name}\n" + "\t" * depth
        for x in self.arguments:
            ret += x
        ret += "\n"
        ret += self.block.__str__(depth + 1)
        return ret


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
