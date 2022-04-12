from common.piece import Piece
from common.vector import Vector2
from dataclasses import dataclass


@dataclass
class PossibleMove(object):

    piece: Piece
    position: Vector2
    skips: bool

