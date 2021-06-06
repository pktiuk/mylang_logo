from .context import RootContext
from .standard_library.library_functions import PrintFunctionDef
from .standard_library.turtle_object import TurtleConstructor
from .standard_library.drawing.canvas import TurtlePaths


class LogoRootContext(RootContext):
    def __init__(self, definition_dict: dict = None):
        super().__init__()
        self.__init_default_definitions()
        self.canvas = TurtlePaths()
        if definition_dict is None:
            definition_dict = {}
        super()._add_and_verify_definitions(definition_dict)

    def __init_default_definitions(self):
        self.definitions["print"] = PrintFunctionDef()
        self.definitions["println"] = PrintFunctionDef("\n")
        self.definitions["Turtle"] = TurtleConstructor(self)
        self.definitions["False"] = False
        self.definitions["True"] = True

    def get_definition(self, name):
        return self.definitions.get(name)

    def get_root_context(self):
        return self
