import pytest
from snake.game import AxisCalc, MatrixDimension


@pytest.mark.parametrize("current_position, steps, expected", [
    (3, -1, 2),
    (3, -2, 1),
    (3, -3, 0),
    (2, -1, 1),
    (2, -2, 0),
    (1, -1, 0)
])
def test_decrease_and_didnt_overflow(current_position: int, steps: int, expected: int):
    matrix_dimension = MatrixDimension(x=4, y=4)
    result = AxisCalc.move_axis(
        current_position=current_position, axis='y', matrix_dimension=matrix_dimension, steps=steps)
    assert result == expected


@pytest.mark.parametrize("current_position, steps, expected", [
    (0, -1, 3),
    (0, -2, 2),
    (0, -3, 1),
    (1, -2, 3),
    (1, -3, 2),
    (2, -3, 3),
])
def test_decrease_and_overflow(current_position: int, steps: int, expected: int):
    matrix_dimension = MatrixDimension(x=4, y=4)
    result = AxisCalc.move_axis(
        current_position=current_position, axis='y', matrix_dimension=matrix_dimension, steps=steps)
    assert result == expected


@pytest.mark.parametrize("current_position, steps, expected", [
    (0, 1, 1),
    (0, 2, 2),
    (0, 3, 3),
    (1, 1, 2),
    (1, 2, 3),
    (2, 1, 3)
])
def test_increase_and_didnt_overflow(current_position: int, steps: int, expected: int):

    matrix_dimension = MatrixDimension(x=4, y=4)
    result = AxisCalc.move_axis(
        current_position=current_position, axis='y', matrix_dimension=matrix_dimension, steps=steps)
    assert result == expected


@pytest.mark.parametrize("current_position, steps, expected", [
    (0, 4, 0),
    (0, 10, 2),
    (2, 15, 1),
    (3, 1, 0),
])
def test_increase_and_overflow(current_position: int, steps: int, expected: int):
    matrix_dimension = MatrixDimension(x=4, y=4)
    result = AxisCalc.move_axis(
        current_position=current_position, axis='y', matrix_dimension=matrix_dimension, steps=steps)
    assert result == expected
