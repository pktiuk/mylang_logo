from ..shared import ConsoleLogger, Location

from ..base_nodes import BaseFunctionDefinition, BaseValue


class PrintFunctionDef(BaseFunctionDefinition):
    def __init__(self, end=""):
        super().__init__(Location(0, 0), "print")
        self.end = end

    def execute(self, values: list, root_context):
        self.validate_arguments(values, 1)
        ConsoleLogger().log(str(values[0]), end=self.end)
