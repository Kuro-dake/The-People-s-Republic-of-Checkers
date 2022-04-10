from Piece import Piece
from Vector2 import Vector2
from dataclasses import dataclass


@dataclass
class PossibleMove(object):

    piece: Piece
    position: Vector2
    skips: bool

