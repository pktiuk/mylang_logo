from .shared import ConsoleLogger
from .language_errors import RuntimeError


class Context:
    def __init__(self, definitions=[], parent_context=None):
        self.parent = parent_context
        self.definitions = {}
        self.elements = {}
        for el in definitions:
            self.definitions[el.name] = el

        self.log = ConsoleLogger()

    def define_element(self, name, value):
        """define new element or redefine old one
        """
        if name in self.definitions.keys():
            raise RuntimeError("Redefinition of element")

        self.elements[name] = value
        #TODO check parent

    def get_element(self, name):
        if name in self.definitions.get(name):
            return self.definitions.get(name)
        else:
            return self.elements.get(name)
