from abc import ABC, abstractmethod

from .canvas import TurtlePaths


class Renderer(ABC):
    def __init__(self, paths: TurtlePaths):
        super().__init__()
        self.paths = paths

    @abstractmethod
    def render(self):
        pass
