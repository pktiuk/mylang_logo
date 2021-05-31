from .shared import Location
from .context import Context, RootContext
from .language_errors import RuntimeError
from .node_classes import Block


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

    def execute(self, values, root_context=RootContext()):
        elements = {}
        if len(values) != len(self.arguments):
            raise RuntimeError("Numbers of arguments don't match")
        for name, value in zip(self.arguments, values):
            elements[name] = value

        new_context = Context(elements=elements, parent_context=root_context)
        result = self.block.evaluate(new_context)
        return result
