from abc import ABC, abstractmethod

from .shared import Location
from .context import Context


class Definition:
    def __init__(self, loc: Location, name: str):
        self.location = loc
        self.name = name


class BaseFunctionDefinition(Definition):
    def __init__(self, loc: Location, name: str):
        super().__init__(loc, name)


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