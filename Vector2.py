from __future__ import annotations

import math


class Vector2(object):

    def __init__(self, x: int, y: int):
        self.x: int = x
        self.y: int = y

    def __add__(self, to_add: Vector2):
        return Vector2(self.x + to_add.x, self.y + to_add.y)

    def __sub__(self, to_sub: Vector2):
        return Vector2(self.x - to_sub.x, self.y - to_sub.y)

    def __mul__(self, other: int):
        if type(other) is not int and type(other) is not float:
            raise Exception("Logic for multiplying of position and {0} is not implemented.".format(type(other)))
        return Vector2(self.x * other, self.y * other)

    def __eq__(self, other: Vector2):
        if type(other) is not Vector2:
            raise Exception("Cannot compare position to any other type")
        # auto convert alphanumeric position string to position
        # this might cause a lot of pain for more or less obv reasons,
        # but I'm keeping the code because I liked the initial idea
        # if type(other) is str:
        #    other = Position.create_from_alphanumeric(other)
        return self.x == other.x and self.y == other.y

    def __neq__(self, other: Vector2):
        return self.x != other.x or self.y != other.y

    def __repr__(self):
        return "Vector2({0},{1})".format(self.x, self.y)

    @property
    def array(self):
        return [self.x, self.y]

    @property
    def direction(self) -> Vector2:
        return Vector2(1 if self.x >= 1 else -1, 1 if self.y >= 1 else -1)

    @property
    def size(self):
        return Vector2(math.fabs(self.x), math.fabs(self.y))

    @property
    def is_diagonal(self):
        return self.size.x == self.size.y

    @staticmethod
    def from_position_query(pos: str):
        return Vector2(ord(pos[0].upper()) - 64, int(pos[1]))

    one = None
    zero = None
    lef = None
    right = None
    up = None
    down = None

    @staticmethod
    def initialize():
        Vector2.one = Vector2(1, 1)
        Vector2.zero = Vector2(0, 0)
        Vector2.left = Vector2(-1, 0)
        Vector2.right = Vector2(1, 0)
        Vector2.up = Vector2(0, -1)
        Vector2.down = Vector2(0, 1)