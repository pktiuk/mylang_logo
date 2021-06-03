from ..shared import ConsoleLogger, Location

from ..base_nodes import BaseFunctionDefinition, BaseValue


class PrintFunctionDef(BaseFunctionDefinition):
    def __init__(self):
        super().__init__(Location(0, 0), "print")

    def execute(self, values: list, root_context):
        self.validate_arguments(values, 1)
        ConsoleLogger().log(str(values[0]))
