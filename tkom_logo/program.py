from .shared import ConsoleLogger
from .root_context import LogoRootContext


class Program(object):
    def __init__(self, definitions: list = None, statements: list = None):
        self.definitions = definitions
        self.statements = statements

        def_dict = {}
        for el in self.definitions:
            def_dict[el.name] = el
        self.root_context = LogoRootContext(def_dict)

        self.log = ConsoleLogger()

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

    def get_canvas(self):
        return self.root_context.canvas
