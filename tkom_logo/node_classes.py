from __future__ import annotations

from .shared import Location
from .context import Context, RootContext
from .language_errors import RuntimeError


class Statement:
    def __init__(self, loc: Location):
        self.location = loc

    def evaluate(self, context: Context):
        raise NotImplementedError


class Expression(Statement):
    def __init__(self, loc: Location):
        super().__init__(loc)

    def get_value(self):
        raise NotImplementedError

    def evaluate(self, context: Context):
        raise NotImplementedError


class ValueAssignment(Statement):
    def __init__(self, loc, name, expression: Expression):
        super().__init__(loc)
        self.name = name
        self.expression = expression

    def __str__(self, depth=0):
        return depth * "\t" + self.name + "=\n" + self.expression.__str__(
            depth + 1)

    def evaluate(self, context: Context):
        result = self.expression.evaluate(context)
        context.define_element(self.name, result)


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
        res += "\t" * depth + self.factors[-1].__str__()

        return res

    def evaluate(self, context: Context):
        result = self.factors[0].evaluate(context)
        iter_nr = 1
        while iter_nr <= len(self.operators):
            operator = self.operators[iter_nr - 1]
            mult_el = self.factors[iter_nr].evaluate(context)
            if operator == "*":
                result *= mult_el
            elif operator == "/":
                if mult_el == 0:
                    raise ZeroDivisionError(
                        f"Dividing by zero at {self.factors[iter_nr].location}"
                    )
                result /= mult_el
            else:
                raise RuntimeError(f"Unexpected add operator: {operator}",
                                   self)
            iter_nr += 1
        return result


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

    def evaluate(self, context: Context):
        result = self.add_expressions[0].evaluate(context)
        iter_nr = 1
        while iter_nr <= len(self.operators):
            operator = self.operators[iter_nr - 1]
            add_el = self.add_expressions[iter_nr].evaluate(context)
            if operator == "+":
                result += add_el
            elif operator == "-":
                result -= add_el
            else:
                raise RuntimeError(f"Unexpected add operator: {operator}",
                                   self)
            iter_nr += 1
        return result


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

    def evaluate(self, context: Context):
        result = self.value.evaluate(context)
        if self.unary_op == '-':
            result = -result
        elif self.unary_op == '!':
            result = not result
        return result


class BaseValue(Expression):
    def __init__(self, loc: Location):
        super().__init__(loc)


class BaseLogicalExpression(Expression):
    def __init__(self, loc: Location):
        super().__init__(loc)


class LogicalExpression(BaseLogicalExpression):
    def __init__(self, and_conditions: list):
        super().__init__(and_conditions[0].location)
        self.and_conditions = and_conditions

    def __str__(self, depth=0):
        res = "\t" * depth + "||\n"
        for cond in self.and_conditions:
            res += cond.__str__(depth + 1)
        return res

    def evaluate(self, context: Context):
        return not all([not x.evaluate(context) for x in self.and_conditions])


class Relation(BaseLogicalExpression):
    def __init__(self, left: MathExpression, right: MathExpression, comp_sign):
        super().__init__(left.location)
        self.left = left
        self.right = right
        self.comp_sign = comp_sign

    def __str__(self, depth=0):
        res = "\t" * depth + self.comp_sign + "\n"
        res += self.left.__str__(depth + 1)
        res += self.right.__str__(depth + 1)
        return res

    def evaluate(self, context: Context):
        COMP_OPERATIONS = {
            "==": lambda l, r: l == r,
            ">=": lambda l, r: l >= r,
            "<=": lambda l, r: l <= r,
            ">": lambda l, r: l > r,
            "<": lambda l, r: l < r,
        }
        left = self.left.evaluate(context)
        right = self.right.evaluate(context)
        return COMP_OPERATIONS[self.comp_sign](left, right)


class AndCondition(BaseLogicalExpression):
    def __init__(self, relations: list):
        super().__init__(relations[0].location)
        self.relations = relations

    def __str__(self, depth=0):
        res = "\t" * depth + "&&\n"
        for cond in self.relations:
            res += cond.__str__(depth + 1)
        return res

    def evaluate(self, context: Context):
        return all([x.evaluate(context) for x in self.relations])


class FieldOperator:
    def __init__(self, loc: Location, name):
        self.location = loc
        self.name = name

    def __str__(self, depth=0):
        return "\t" * depth + f". {self.name}"

    def evaluate(self, context: Context, source_element):
        pass  # TODO Dodaj typ obiektu


class FunOperator:
    def __init__(self, loc: Location, arguments):
        self.location = loc
        self.arguments = arguments

    def __str__(self, depth=0):
        ret = "\t" * depth + "()\n"
        for arg in self.arguments:
            ret += arg.__str__(depth + 1)
        return ret

    def evaluate(self, context: Context, source_element: 'FunctionDefinition'):
        values = [x.evaluate(context) for x in self.arguments]
        result = source_element.execute(values, context.get_root_context())
        return result


class Identifier(BaseValue):
    def __init__(self, loc: Location, name: str):
        super().__init__(loc)
        self.name = name

    def __str__(self, depth=0):
        return "\t" * depth + self.name + "\n"

    def evaluate(self, context: Context):
        result = context.get(self.name)
        if result is None:
            raise RuntimeError(
                f"Trying to access undefined variable (named {self.name})",
                self)
        return result


class Value(BaseValue):
    def __init__(self, id_value: Identifier, operators=None):
        super().__init__(id_value.location)
        self.id_value = id_value
        if operators:
            self.operators = operators
        else:
            self.operators = []

    def __str__(self, depth=0):
        res = ""
        for op in reversed(self.operators):
            res += op.__str__(depth)
            depth = depth + 1
        res += "\t" * depth + self.id_value.name + "\n"
        return res

    def evaluate(self, context: Context):
        result = self.id_value.evaluate(context)

        for operator in self.operators:
            result = operator.evaluate(context, result)

        return result


class ConstValue(BaseValue):
    def __init__(self, loc: Location, value):
        super().__init__(loc)
        self.value = value

    def __str__(self, depth=0):
        return "\t" * depth + str(self.value) + "\n"

    def evaluate(self, context: Context):
        return self.value


class Block(object):
    def __init__(self, statements: list):
        self.statements = statements

    def __str__(self, depth=0):
        res = depth * "\t" + "BLOCK\n"
        for statement in self.statements:
            res += statement.__str__(depth + 1)
        return res

    def evaluate(self, context: Context):
        for statement in self.statements:
            statement.evaluate(context)


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

    def evaluate(self, context: Context):
        cond_value = self.condition.evaluate(context)
        if_context = Context(parent_context=context)
        if (cond_value):
            self.true_block.evaluate(if_context)
        elif self.false_block:
            self.false_block.evaluate(if_context)


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

    def evaluate(self, context: Context):
        cond_value = self.condition.evaluate(context)
        while_context = Context(parent_context=context)
        while cond_value:
            self.block.evaluate(while_context)
            cond_value = self.condition.evaluate(while_context)
