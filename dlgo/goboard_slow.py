import copy
from dlgo.gotypes import Player


class Move:
    # Any action a player can play on a turn -
    # is_play, is_pass, or is_resign - will be set.
    def __init__(self, point=None, is_pass=False, is_resign=False):
        assert (point is not None) ^ is_pass ^ is_resign
        self.point = point
        self.is_play = (self.point is not None)
        self.is_pass = is_pass
        self.is_resign = is_resign

    # This move places a stone on the board.
    @classmethod
    def play(cls, point):
        return Move(point=point)

    # This move passes.
    @classmethod
    def pass_turn(cls):
        return Move(is_pass=True)

    # This move resigns the current game.
    @classmethod
    def resign(cls):
        return Move(is_resign=True)


class GoString:
    # Go stings are a chain of connected stones of the same color.
    def __init__(self, color, stones, liberties):
        self.color = color
        self.stones = stones
        self.liberties = set(liberties)

    def remove_liberty(self, point):
        self.liberties.remove(point)

    def add_liberty(self, point):
        self.liberties.add(point)

    def merged_with(self, go_string):
        # Returns a new Go string containing all stones in both strings
        assert go_string.color == self.color
        combined_stones = self.stones | go_string.stones
        return GoString(
            self.color,
            combined_stones,
            (self.liberties | go_string.liberties) - combined_stones
        )

    @property
    def num_liberties(self):
        return len(self.liberties)

    def __eq__(self, other):
        return isinstance(other, GoString) and \
            self.color == other.color and \
            self.stones == other.stones and \
            self.liberties == other.liberties


