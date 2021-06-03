from __future__ import annotations

from ..base_nodes import BaseFunctionDefinition, BaseObject
from ..context import RootContext, Context
from ..shared import Location


class Turtle(BaseObject):
    def __init__(self, canvas=None):  # TODO get_canvas
        self.x = 0
        self.y = 0
        # canvas.draw() # TODO

    def get_field(self, name: str):
        FIELDS = {
            "get_x": GetterFunction(self, "x"),
            "get_y": GetterFunction(self, "y"),
        }
        return FIELDS[name]

    def evaluate(self, context: Context):
        return self

    def __str__(self, depth=0):
        return "\t" * depth + f"Turtle (x: {self.x}, y: {self.y})"


class TurtleConstructor(BaseFunctionDefinition):
    def __init__(self):
        super().__init__(Location(0, 0), "Turtle")

    def execute(self, values: list, root_context: RootContext):
        return Turtle()  # TODO tutaj jakoś przekazuj canvas


class GetterFunction(BaseFunctionDefinition):
    GETTERS = {"x": lambda turtle: turtle.x, "y": lambda turtle: turtle.y}

    def __init__(self, turtle: Turtle, var_name: str):
        self.turtle = turtle
        self.getter = self.GETTERS[var_name]

    def execute(self, values: list, root_context: RootContext):
        return self.getter(self.turtle)
