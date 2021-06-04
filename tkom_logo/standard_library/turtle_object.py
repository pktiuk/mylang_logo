from __future__ import annotations

from math import sin, cos, radians

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
        self.name = "Turtle"

    def get_field(self, name: str):
        FIELDS = {
            "get_x": GetterFunction(self, "x"),
            "get_y": GetterFunction(self, "y"),
            "move": MovementFunction(self),
            "rotate": SetFunction(self, "rotate"),
            "set_angle": SetFunction(self, "angle"),
            "set_x": SetFunction(self, "x"),
            "set_y": SetFunction(self, "y"),
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
        self.validate_arguments(values, 0)
        return Turtle(canvas=self.logo_context.canvas)


class GetterFunction(BaseFunctionDefinition):
    GETTERS = {"x": lambda turtle: turtle.x, "y": lambda turtle: turtle.y}

    def __init__(self, turtle: Turtle, var_name: str):
        super().__init__(name=var_name)
        self.turtle = turtle

    def execute(self, values: list, root_context: RootContext):
        self.validate_arguments(values, 0)
        return self.GETTERS[self.name](self.turtle)


class SetFunction(BaseFunctionDefinition):
    def __init__(self, turtle: Turtle, var_name: str):
        super().__init__(name=var_name)
        self.turtle = turtle

    def execute(self, values: list, root_context: RootContext):
        self.validate_arguments(values, 1)

        if self.name == "x":
            self.turtle.x = values[0]
        elif self.name == "y":
            self.turtle.y = values[0]
        elif self.name == "angle":
            self.turtle.angle = values[0]
            self.turtle.canvas.rotate_turtle(self.turtle.turtle_id, self.turtle.angle)
        elif self.name == "rotate":
            self.turtle.angle = self.turtle.angle + values[0]
            self.turtle.canvas.rotate_turtle(self.turtle.turtle_id, self.turtle.angle)


class MovementFunction(BaseFunctionDefinition):
    def __init__(self, turtle: Turtle):
        super().__init__(name="move")
        self.turtle = turtle

    def execute(self, values: list, root_context: RootContext):
        self.validate_arguments(values, 1)
        id = self.turtle.turtle_id
        canvas = self.turtle.canvas
        distance = values[0]
        x = distance * sin(-radians(self.turtle.angle))
        y = distance * cos(-radians(self.turtle.angle))
        canvas.move_turtle(id, x, y)
        self.turtle.x += x
        self.turtle.y += y
