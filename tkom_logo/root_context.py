from .context import RootContext
from .standard_library.library_functions import PrintFunctionDef
from .standard_library.turtle_object import TurtleConstructor
from .standard_library.drawing.canvas import TurtlePaths


class LogoRootContext(RootContext):
    def __init__(self, definition_dict: dict = None):
        super().__init__(definitions=definition_dict)
        self.__init_default_definitions()
        self.canvas = TurtlePaths()

    def __init_default_definitions(self):
        self.definitions["print"] = PrintFunctionDef()
        self.definitions["Turtle"] = TurtleConstructor(self)

    def get_definition(self, name):
        return self.definitions.get(name)

    def get_root_context(self):
        return self
