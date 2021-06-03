from .context import BaseRootContext
from .standard_library.library_functions import PrintFunctionDef


class RootContext(BaseRootContext):
    def __init__(self, definition_dict: dict = None):
        super().__init__(definitions=definition_dict)
        self.__init_default_definitions()

    def __init_default_definitions(self):
        self.definitions["print"] = PrintFunctionDef()
        pass

    def get_definition(self, name):
        return self.definitions.get(name)

    def get_root_context(self):
        return self