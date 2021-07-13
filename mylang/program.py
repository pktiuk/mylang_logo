from .shared import global_logger
from .root_context import LogoRootContext
from .language_errors import LogoRuntimeError


class Program(object):
    def __init__(self, definitions: list = None, statements: list = None):
        self.definitions = definitions
        self.statements = statements

        def_dict = {}
        for el in self.definitions:
            def_dict[el.name] = el
        self.root_context = LogoRootContext(def_dict)

        self.log = global_logger
        self.current_statement = None

    def __str__(self):
        ret = "Definitions:\n"
        for d in self.definitions:
            ret += d.__str__(1)
        ret += "Statements:\n"
        for d in self.statements:
            ret += d.__str__(1)
        return ret

    def _decorate_exception(decorated_fun, *args, **kwargs):
        def output_fun(*args, **kwargs):
            try:
                t = decorated_fun(*args, **kwargs)
            except LogoRuntimeError as err:
                if err.location is None:
                    err.location = args[0].current_statement.location
                raise err
            except TypeError as err:
                TYPES = [
                    "str", "bool", "Turtle", "float", "FunctionDefinition"
                ]
                # default message format:
                # TypeError: unsupported operand type(s) for +=: 'bool' and 'str'
                msg = err.args[0].split("'")
                type1 = msg[-2]
                type2 = msg[-4]
                if type1 in TYPES and type2 in TYPES:
                    raise LogoRuntimeError(
                        f"Unsupported operation for types {type1} and {type2}",
                        args[0].current_statement.location)
                else:
                    raise err
            return t

        return output_fun

    @_decorate_exception
    def execute(self):
        for statement in self.statements:
            self.current_statement = statement
            statement.evaluate(self.root_context)

    def get_canvas(self):
        return self.root_context.canvas
