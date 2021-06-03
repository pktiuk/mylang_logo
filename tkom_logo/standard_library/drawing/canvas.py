class TurtlePaths():
    def __init__(self):
        self.turtle_lines = {}
        self.turtle_angles = {}
        self.next_id = 0

    def add_turtle(self, x1: int = 0, y1: int = 0) -> int:
        "returns turtle ID"
        self.turtle_lines[self.next_id] = [(x1, y1)]
        self.turtle_angles[self.next_id] = 0
        self.next_id += 1
        return self.next_id - 1

    def move_turtle(self, turtle_id: int, x: int, y: int):
        old_x, old_y = self.turtle_lines[turtle_id][-1]
        self.turtle_lines[turtle_id].append((old_x + x, old_y + y))

    def rotate_turtle(self, turtle_id: int, angle: float):
        self.turtle_angles[turtle_id] = angle
