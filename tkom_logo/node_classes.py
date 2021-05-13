from .shared import Location


class Program(object):
    def __init__(self):
        self.definitions_list = []
        self.statements = []


class Statement:
    def __init__(self, loc: Location):
        self.location = loc


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


class LogicalExpression(Expression):
    def __init__(self, loc: Location):
        super().__init__(loc)


class Comparison(LogicalExpression):
    def __init__(self, left: Expression, right: Expression, comp_sign):
        super().__init__(left.location)
        self.left = left
        self.right = right
        self.comp_sign = comp_sign

    def __str__(self, depth=0):
        return ""


class AndCondition(LogicalExpression):
    def __init__(self, left: Comparison, right: 'AndCondition'):
        super().__init__(left.location)
        self.left = left
        self.right = right

    def __str__(self, depth=0):
        return ""


class OrCondition(LogicalExpression):
    def __init__(self, left: AndCondition, right: 'OrCondition'):
        super().__init__(left.location)
        self.left = left
        self.right = right

    def __str__(self, depth=0):
        return ""


class FieldOperator:
    def __init__(self, loc: Location, name):
        self.location = loc
        self.name = name

    def __str__(self, depth=0):
        return "\t" * depth + f". {self.name}"


class FunOperator:
    def __init__(self, loc: Location, arguments):
        self.location = loc
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