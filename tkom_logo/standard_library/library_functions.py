from ..shared import ConsoleLogger, Location

from ..base_nodes import BaseFunctionDefinition


class PrintFunctionDef(BaseFunctionDefinition):
    def __init__(self):
        super().__init__(Location(0, 0), "print")

    def execute(self, values: list, root_context):
        if len(values) != 1:
            raise RuntimeError("Print function requires one argument")
        ConsoleLogger().log(str(values[0]))
