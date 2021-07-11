from abc import ABC, abstractmethod

from .shared import Location
from .context import Context, RootContext
from .language_errors import LogoRuntimeError


class Definition(ABC):
    def __init__(self, loc: Location, name: str):
        self.location = loc
        self.name = name

    def __str__(self, depth=0):
        return depth * "\t" + self.name + "\n"


class BaseFunctionDefinition(Definition):
    def __init__(self, loc: Location = Location(0, 0), name: str = ""):
        super().__init__(loc, name)

    @abstractmethod
    def execute(self, values: list, root_context: RootContext):
        pass

    def validate_arguments(self, values: list, min=0, max=None, msg=None):
        if max is None:
            max = min
        val_len = len(values)
        if msg is None:
            msg = f"wrong number of arguments passed to function {self.name} {val_len}"
            if max == min:
                msg += f" instead of expected {min}"
        if not (max >= val_len >= min):
            raise LogoRuntimeError(msg)


class Statement(ABC):
    def __init__(self, loc: Location):
        self.location = loc

    @abstractmethod
    def evaluate(self, context: Context):
        raise NotImplementedError


class Expression(Statement):
    def __init__(self, loc: Location):
        super().__init__(loc)

    def evaluate(self, context: Context):
        raise NotImplementedError


class BaseValue(Expression):
    def __init__(self, loc: Location):
        super().__init__(loc)

    @abstractmethod
    def __str__(self, depth=0):
        pass

    @abstractmethod
    def evaluate(self, context: Context):
        pass


class BaseObject(ABC):
    @abstractmethod
    def get_field(self, name: str):
        pass

    @abstractmethod
    def evaluate(self, context: Context):
        pass
