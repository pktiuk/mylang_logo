from .shared import ConsoleLogger
from .language_errors import RuntimeError


class Context:
    def __init__(self, definition_list=[], elements={}, parent_context=None):
        self.parent = parent_context
        self.definitions = {}
        self.elements = elements
        for el in definition_list:
            self.definitions[el.name] = el

        self.log = ConsoleLogger()

    def define_element(self, name, value):
        """define new element or redefine old one
        """
        if name in self.definitions.keys():
            raise RuntimeError("Redefinition of element")

        existing_element = self.elements.get(name)
        if not existing_element and self.parent:
            existing_element = self.parent.get_element(name)
            if existing_element:
                self.parent.define_element(name, value)
                return
        self.elements[name] = value

    def get_element(self, name):
        result = self.elements.get(name)

        if not result and self.parent:
            return self.parent.get_element(name)
        else:
            return result

    def get_definition(self, name):
        return self.parent.get_definition(name)

    def __str__(self):
        ret = "CONTEXT:\nDefinitions:\n"
        for defn in self.definitions:
            ret += defn.__str__(depth=1)
        ret += "\nElements:\n"
        for name, value in self.elements.items():
            ret += "\t" + name + " = " + str(value) + "\n"
        return ret


class RootContext(Context):
    def __init__(self, definition_list=[]):
        super().__init__(definition_list)
        self.__init_default_definitions()

    def __init_default_definitions(self):
        pass

    def get_definition(self, name):
        return self.definitions.get(name)