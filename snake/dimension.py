direction_axis = {"up": "y", "down": "y", "left": "x", "right": "x"}

oposite_direction = {"up": "down", "down": "up", "left": "right", "right": "left"}

constants = {"up": -1, "down": 1, "left": -1, "right": 1}


all_directions = {1: "up", 2: "down", 3: "left", 4: "right"}


class MatrixDimension:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def get_axis_size(self, direction: str) -> int:
        if self.get_axis(direction) == "x":
            return self.x
        if self.get_axis(direction) == "y":
            return self.y

    def get_axis(self, direction: str) -> str:
        return direction_axis[direction]

    def revert_direction(self, direction: str) -> str:
        return oposite_direction.get(direction, None)
