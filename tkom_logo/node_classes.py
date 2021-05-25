from .shared import Location


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
        return depth * "\t" + self.name + "=\n" + self.expression.__str__(
            depth + 1)


class AddExpression(Expression):
    def __init__(self, factors: list, operators: list):
        super().__init__(factors[0].location)
        self.operators = operators
        self.factors = factors

    def __str__(self, depth=0):
        res = "\t" * depth + self.operators[0] + "\n"
        depth += 1
        res += self.factors[0].__str__(depth)
        iter_nr = 1
        while iter_nr < len(self.operators):
            res += "\t" * depth + self.operators[iter_nr] + "\n"
            depth += 1
            res += self.factors[iter_nr].__str__(depth)
            iter_nr += 1
        res += "\t" * depth + self.factors.__str__()

        return res


class MathExpression(Expression):
    def __init__(self, add_expressions, operators):
        super().__init__(add_expressions[0].location)
        self.operators = operators
        self.add_expressions = add_expressions

    def __str__(self, depth=0):
        res = "\t" * depth + self.operators[0] + "\n"
        depth += 1
        res += self.add_expressions[0].__str__(depth)
        iter_nr = 1
        while iter_nr < len(self.operators):
            res += "\t" * depth + self.operators[iter_nr] + "\n"
            depth += 1
            res += self.add_expressions[iter_nr].__str__(depth)
            iter_nr += 1
        res += "\t" * depth + self.add_expressions[-1].__str__() + "\n"

        return res


class Factor(Expression):
    def __init__(self, value, unary_op=None):
        super().__init__(value.location)
        self.unary_op = unary_op
        self.value = value

    def __str__(self, depth=0):

        if self.unary_op:
            return depth * "\t" + self.unary_op + self.value.__str__()
        else:
            return self.value.__str__(depth)


class Value(Expression):
    def __init__(self, loc: Location):
        super().__init__(loc)


class BaseLogicalExpression(Expression):
    def __init__(self, loc: Location):
        super().__init__(loc)


class LogicalExpression(BaseLogicalExpression):
    def __init__(self, and_conditions: list, unary_op=None):
        super().__init__(and_conditions[0].location)
        self.and_conditions = and_conditions
        self.unary_op = unary_op

    def __str__(self, depth=0):
        res = "\t" * depth + "||\n"
        for cond in self.and_conditions:
            res += cond.__str__(depth + 1)
        return res


class Relation(BaseLogicalExpression):
    def __init__(self, left: MathExpression, right: MathExpression, comp_sign):
        super().__init__(left.location)
        self.left = left
        self.right = right
        self.comp_sign = comp_sign

    def __str__(self, depth=0):
        return ""


class AndCondition(BaseLogicalExpression):
    def __init__(self, relations: list):
        super().__init__(relations[0].location)
        self.relations = relations

    def __str__(self, depth=0):
        res = "\t" * depth + "&&\n"
        for cond in self.relations:
            res += cond.__str__(depth + 1)
        return res


class OrCondition(BaseLogicalExpression):
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
        ret = "\t" * depth + "()\n"
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
                 condition: BaseLogicalExpression,
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
    def __init__(self, loc: Location, condition: BaseLogicalExpression,
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


class Program(object):
    def __init__(self, definitions=[], statements=[]):
        self.definitions = definitions
        self.statements = statements

    def __str__(self):
        ret = "Definitions:\n"
        for d in self.definitions:
            ret += d.__str__(1)
        ret += "Statements:\n"
        for d in self.statements:
            ret += d.__str__(1)
        return ret
