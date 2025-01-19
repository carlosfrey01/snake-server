import json
import random
import time
from enum import Enum
from queue import Queue
from threading import Thread

import numpy as np
from dimension import MatrixDimension, all_directions


class Snake:
    def __init__(
        self, dimension: MatrixDimension, body_size: int = 5, input_queue_size: int = 10
    ):
        self.dimension: MatrixDimension = dimension
        self.current_direction: str = "up"
        self.score = 0
        self.snake_body = []
        self.has_collision = False
        self.last_tail_position = None
        self.current_tail_position = None
        self.body_size = body_size
        self.had_meal = False
        self.matrix_queue = Queue(maxsize=1)
        self.matrix = np.full((self.dimension.x, self.dimension.y), 0, dtype=object)
        self.input_queue = Queue(maxsize=input_queue_size)

    def move_axis(self, current_position: int, direction: str) -> int:
        axis_size = self.dimension.get_axis_size(direction)

        if direction == "up" or direction == "left":
            decrease_index_result = current_position - 1
            has_overflow: bool = decrease_index_result < 0
            if has_overflow:
                return axis_size - 1
            return decrease_index_result

        if direction == "right" or direction == "down":
            increase_index_result = current_position + 1
            last_index = axis_size - 1
            has_overflow: bool = increase_index_result > last_index

            if has_overflow:
                return 0
            return increase_index_result

    def change_direction(self, key):
        if key == "up":
            self.input_queue.put("up")
        if key == "down":
            self.input_queue.put("down")
        if key == "left":
            self.input_queue.put("left")
        if key == "right":
            self.input_queue.put("right")

    def generate_random_position(self) -> dict:
        return {
            "x": random.randint(0, self.dimension.x - 1),
            "y": random.randint(0, self.dimension.y - 1),
        }

    def create_snake(self):
        distribution_direction = self.generate_random_direction()
        self.current_direction = distribution_direction

        head = self.generate_random_position()

        head["type"] = "body"
        head["direction"] = distribution_direction
        appending_items = self.body_size - 1
        self.snake_body = self.generate_snake_body(
            head=head, appending_items=appending_items
        )

    def generate_snake_body(self, append_mode=False, head=None, appending_items=1):
        coordinate_type = "body"
        new_snake = []

        if append_mode:
            new_snake.append(head)

        distribution_direction = head["direction"]
        reverted_direction = self.dimension.revert_direction(distribution_direction)

        axis = self.dimension.get_axis(reverted_direction)
        current_axis_position = head[axis]

        for _ in range(appending_items):
            result = self.move_axis(
                current_position=current_axis_position, direction=reverted_direction
            )
            body_part = {
                **head,
                axis: result,
                "type": coordinate_type,
                "direction": distribution_direction,
            }
            current_axis_position = result
            new_snake.append(body_part)
        return new_snake

    def move_snake(self):
        if not self.had_meal:
            parsing_position = None
            tail_index = len(self.snake_body) - 1
            for index, part in enumerate(self.snake_body):
                axis = self.dimension.get_axis(self.current_direction)
                if index == 0:
                    previous_position = part
                    current_axis_position = part[axis]
                    new_axis_position = self.move_axis(
                        current_position=current_axis_position,
                        direction=self.current_direction,
                    )
                    new_cordinates = {
                        **previous_position,
                        axis: new_axis_position,
                        "direction": self.current_direction,
                    }
                    self.snake_body[index] = new_cordinates
                    parsing_position = previous_position

                    if index == tail_index:
                        self.last_tail_position = part
                elif index == tail_index:
                    self.snake_body[index] = parsing_position
                    self.last_tail_position = part
                else:
                    self.snake_body[index] = parsing_position
                    parsing_position = part
        else:
            self.had_meal = False

    def generate_random_direction(self):
        number = random.randint(1, 4)
        return all_directions[number]

    def read_and_validate_input(self):
        if not self.input_queue.empty():
            direction = self.input_queue.get()
            if self.dimension.revert_direction(self.current_direction) != direction:
                previous = self.current_direction
                self.current_direction = direction
                current = self.current_direction
                print(
                    f"previous: {previous}\ncurrent:{current} inserting direction: {direction}"
                )

    def generate_food(self):
        while True:
            food_position = self.generate_random_position()
            x = food_position["x"]
            y = food_position["y"]

            self.matrix[y][x] = {"type": "food", "bonus": 1}
            time.sleep(3)

    def generate_food_thread(self):
        thread = Thread(target=self.generate_food)
        thread.start()

    def verify_collision_in_matrix(self):
        head = self.snake_body[0]
        axis = self.dimension.get_axis(self.current_direction)
        current_position = head[axis]
        new_position = self.move_axis(
            current_position=current_position, direction=self.current_direction
        )
        next_position = {**head, axis: new_position}
        x = next_position["x"]
        y = next_position["y"]

        predicted_position = self.matrix[y][x]

        if predicted_position:
            predicted_type = predicted_position["type"]
            if predicted_type == "food":
                bonus = predicted_position["bonus"]
                self.snake_body.insert(0, next_position)
                self.body_size += 1
                self.had_meal = True
                self.matrix[y][x] = self.snake_body[0]
                if bonus > 1:
                    bonus_after_tail = bonus - 1
                    tail = self.snake_body[-1]
                    x = tail["x"]
                    y = tail["y"]

                    incrementing_body = self.generate_snake_body(
                        append_mode=True, head=tail, appending_items=bonus_after_tail
                    )
                    self.snake_body.append(incrementing_body)

            if predicted_type == "body":
                tail = self.snake_body[-1]
                if predicted_position != tail:
                    self.has_collision = True
                    self.game_thread.pause()

    def update_matrix(self):
        if self.last_tail_position:
            tail = self.last_tail_position
            x = tail["x"]
            y = tail["y"]
            self.matrix[y][x] = 0

        for part in self.snake_body:
            x = part["x"]
            y = part["y"]
            self.matrix[y][x] = part

    def add_updated_snake_to_queue(self):
        matrix = self.get_and_parse_matrix()
        self.matrix_queue.put(matrix)

    def get_and_parse_matrix(self):
        payload = {"name": "update_matrix", "payload": self.matrix.tolist()}
        return json.dumps(payload)

    def game_start(self, event):
        self.create_snake()
        self.update_matrix()
        self.generate_food_thread()
        while True:
            self.add_updated_snake_to_queue()
            time.sleep(0.2)
            self.read_and_validate_input()
            self.verify_collision_in_matrix()
            event.wait()
            self.move_snake()
            self.update_matrix()


if __name__ == "__main__":
    dimension = MatrixDimension(x=10, y=10)
    snake = Snake(dimension=dimension, body_size=7)
    head = snake.generate_random_position()
    head = {**head, "direction": "right"}
    result = snake.generate_snake_body(append_mode=True, head=head, appending_items=5)
    print(result)
    print(len(result))
