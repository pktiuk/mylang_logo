from .shared import ConsoleLogger
from .context import Context


class Program(object):
    def __init__(self, definitions=[], statements=[]):
        self.definitions = definitions
        self.statements = statements

        self.root_context = Context(self.definitions)
        self.log = ConsoleLogger()
        self.program = None
        self.canvas = None  # TODO

    def __str__(self):
        ret = "Definitions:\n"
        for d in self.definitions:
            ret += d.__str__(1)
        ret += "Statements:\n"
        for d in self.statements:
            ret += d.__str__(1)
        return ret

    def execute(self):
        for statement in self.statements:
            statement.evaluate(self.root_context)
