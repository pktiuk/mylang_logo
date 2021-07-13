from .shared import global_logger
from .language_errors import LogoRuntimeError


class Context:
    def __init__(self,
                 definitions: dict = None,
                 elements: dict = None,
                 parent_context=None):
        self.parent = parent_context

        if definitions:
            self.definitions = definitions
        else:
            self.definitions = {}

        if elements:
            self.elements = elements
        else:
            self.elements = {}

        self.log = global_logger

    def define_element(self, name, value):
        """define new element or redefine old one
        """
        if name in self.definitions.keys():
            raise LogoRuntimeError("Redefinition of element")

        local_element = self.elements.get(name)
        if local_element is None and self.parent:
            parent_element = self.parent.get_element(name)
            if parent_element is not None:
                self.parent.define_element(name, value)
                return
        self.elements[name] = value

    def _add_and_verify_definitions(self, definitions: dict):
        for name, value in definitions.items():
            if self.definitions.get(name):
                raise LogoRuntimeError("Redefinition of function: ", name)
            self.definitions[name] = value

    def get_element(self, name):
        result = self.elements.get(name)

        if result is None and self.parent:
            return self.parent.get_element(name)
        else:
            return result

    def get(self, name):
        "returns element or definition"
        if (result := self.get_element(name)) is not None:
            return result
        else:
            return self.get_definition(name)

    def get_definition(self, name):
        if definition := self.definitions.get(name):
            return definition
        else:
            return self.parent.get_definition(name)

    def get_root_context(self):
        if self.parent:
            return self.parent.get_root_context()

    def __str__(self):
        ret = "CONTEXT:\nDefinitions:\n"
        for defn in self.definitions.values():
            ret += defn.__str__()
        ret += "\nElements:\n"
        for name, value in self.elements.items():
            ret += "\t" + name + " = " + str(value) + "\n"
        return ret


class RootContext(Context):
    pass
