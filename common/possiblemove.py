"""
A basic struct to store the possible moves of a piece
"""

from common.piece import Piece
from common.vector import Vector2
from dataclasses import dataclass


@dataclass
class PossibleMove(object):

    piece: Piece
    position: Vector2
    skips: bool

    def __repr__(self):
        return "{0} {1} {2}".format(self.piece, self.position, self.skips)
