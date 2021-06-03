from .base_nodes import BaseFunctionDefinition
from .shared import Location
from .context import Context, RootContext
from .language_errors import RuntimeError
from .node_classes import Block


class FunctionDefinition(BaseFunctionDefinition):
    class ReturnValue(Exception):
        pass

    class ReturnFunction(BaseFunctionDefinition):
        def __init__(self):
            super().__init__(Location(0, 0), "return")

        def execute(self, values, root_context: Context):
            arg_num = len(values)
            if arg_num > 1:
                raise RuntimeError(
                    f"Wrong number of valuse passed to return: {arg_num}")
            if arg_num:
                raise FunctionDefinition.ReturnValue(values[0])
            else:
                raise FunctionDefinition.ReturnValue(None)

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

    def execute(self, values, root_context: RootContext):
        passed_arguments = {}
        if len(values) != len(self.arguments):
            raise RuntimeError("Numbers of arguments don't match")
        for name, value in zip(self.arguments, values):
            passed_arguments[name] = value

        definitions = {"return": FunctionDefinition.ReturnFunction()}
        new_context = Context(elements=passed_arguments,
                              definitions=definitions,
                              parent_context=root_context)

        result = None
        try:
            self.block.evaluate(new_context)
        except FunctionDefinition.ReturnValue as ret:
            result = ret.args[0]
        return result
