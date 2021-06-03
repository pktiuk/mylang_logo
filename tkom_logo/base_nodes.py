from abc import ABC, abstractmethod

from .shared import Location
from .context import Context, BaseRootContext


class Definition(ABC):
    def __init__(self, loc: Location, name: str):
        self.location = loc
        self.name = name

    def __str__(self, depth=0):
        return depth * "\t" + self.name


class BaseFunctionDefinition(Definition):
    def __init__(self, loc: Location, name: str):
        super().__init__(loc, name)

    @abstractmethod
    def execute(self, values: list, root_context: BaseRootContext):
        pass


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


class BaseObject(ABC):
    @abstractmethod
    def get_field(self, name: str):
        pass
