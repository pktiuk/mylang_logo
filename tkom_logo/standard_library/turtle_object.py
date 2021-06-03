from __future__ import annotations

from math import sin, cos

from ..base_nodes import BaseFunctionDefinition, BaseObject
from ..context import RootContext, Context
from ..shared import Location

from .drawing.canvas import TurtlePaths


class Turtle(BaseObject):
    def __init__(self, canvas: TurtlePaths = None):  # TODO get_canvas
        self.x = 0
        self.y = 0
        self.angle = 0
        self.canvas = canvas
        self.turtle_id = self.canvas.add_turtle()

    def get_field(self, name: str):
        FIELDS = {
            "get_x": GetterFunction(self, "x"),
            "get_y": GetterFunction(self, "y"),
            "move": MovementFunction(self),
        }
        return FIELDS[name]

    def evaluate(self, context: Context):
        return self

    def __str__(self, depth=0):
        return "\t" * depth + f"Turtle (x: {self.x}, y: {self.y} angle: {self.angle})"


class TurtleConstructor(BaseFunctionDefinition):
    def __init__(self, logo_context):
        super().__init__(Location(0, 0), "Turtle")
        self.logo_context = logo_context

    def execute(self, values: list, root_context: RootContext):
        return Turtle(canvas=self.logo_context.canvas)


class GetterFunction(BaseFunctionDefinition):
    GETTERS = {"x": lambda turtle: turtle.x, "y": lambda turtle: turtle.y}

    def __init__(self, turtle: Turtle, var_name: str):
        self.turtle = turtle
        self.getter = self.GETTERS[var_name]

    def execute(self, values: list, root_context: RootContext):
        return self.getter(self.turtle)


class MovementFunction(BaseFunctionDefinition):
    def __init__(self, turtle: Turtle):
        self.turtle = turtle

    def execute(self, values: list, root_context: RootContext):
        id = self.turtle.turtle_id
        canvas = self.turtle.canvas
        distance = values[0]
        x = distance * sin(self.turtle.angle)
        y = distance * cos(self.turtle.angle)
        canvas.move_turtle(id, x, y)
        self.turtle.x += x
        self.turtle.y += y
