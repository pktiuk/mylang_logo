from .shared import ConsoleLogger


class Context:
    def __init__(self, definitions=[], parent_context=None):
        self.parent = parent_context
        self.elements = {}
        for el in definitions:
            self.elements[el.name] = el

        self.log = ConsoleLogger()

    def define_element(self, element):
        pass

    def get_element(self, name):
        pass
