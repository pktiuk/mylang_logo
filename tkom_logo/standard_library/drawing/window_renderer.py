import sys

from .canvas import TurtlePaths
from .renderer import Renderer

from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPen, QBrush, QPainterPath
from PyQt5.QtWidgets import QGraphicsScene, QWidget, QGraphicsView, QVBoxLayout

from PyQt5.QtWidgets import QApplication


class CanvasWidget(QGraphicsScene):
    def __init__(self, *args):
        super(QGraphicsScene, self).__init__(-100, -100, 200, 200, *args)
        self.setBackgroundBrush(QBrush(Qt.gray))

        self.pen = QPen(Qt.black)
        self.turtles = {}  # id:turtle object

    def draw_line(self, x1, y1, x2, y2):
        self.addLine(x1, y1, x2, y2, self.pen)


class WindowRenderer(Renderer):
    def __init__(self, paths: TurtlePaths):
        super().__init__(paths)

    def render(self):
        app = QApplication(sys.argv)

        scene = CanvasWidget()
        w = QWidget()
        view = QGraphicsView()
        view.setScene(scene)
        view.resizeEvent = lambda x: view.fitInView(scene.sceneRect(), Qt.
                                                    KeepAspectRatio)

        layout = QVBoxLayout()
        layout.addWidget(view)
        w.setLayout(layout)

        self.draw_lines(scene)

        w.show()
        sys.exit(app.exec_())

    def draw_lines(self, scene: CanvasWidget):
        for id, turtle_lines in self.paths.turtle_lines.items():
            start_x = None
            start_y = None
            for x, y in turtle_lines:
                if start_x is not None:
                    scene.draw_line(start_x, start_y, x, y)
                start_x = x
                start_y = y
            self.draw_turtle(scene, id, start_x, start_y)

    def draw_turtle(self, scene: CanvasWidget, id, x, y):
        path = QPainterPath(QPointF(0, 0))
        path.lineTo(QPointF(5, -5))
        path.lineTo(QPointF(0, 5))
        path.lineTo(QPointF(-5, -5))
        path.lineTo(QPointF(0, 0))
        turtle = scene.addPath(path, QPen(Qt.blue), QBrush(Qt.red))
        turtle.moveBy(x, y)
        turtle.setRotation(self.paths.turtle_angles[id])
