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
    # Go strings are a chain of connected stones of the same color.
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


class Board:
    # A board is initialized as an empty grid
    # with the specified number of rows and columns.
    def __init__(self, num_rows, num_cols):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self._grid = {}

    def place_stone(self, player, point):
        assert self.is_on_grid(point)
        assert self._grid.get(point) is None
        adjacent_same_color = []
        adjacent_opposite_color = []
        liberties = []
        # First, you examine direct neighbors of this point
        for neighbor in point.neighbors():
            if not self.is_on_grid(neighbor):
                continue
            neighbor_string = self._grid.get(neighbor)
            if neighbor_string is None:
                liberties.append(neighbor_string)
            elif neighbor_string.color == player:
                if neighbor_string not in adjacent_same_color:
                    adjacent_opposite_color.append(neighbor_string)
            else:
                if neighbor_string not in adjacent_opposite_color:
                    adjacent_opposite_color.append(neighbor_string)

        new_string = GoString(player, [point], liberties)
        # merge any adjacent string of the same color.
        for same_color_string in adjacent_same_color:
            new_string = new_string.merged_with(same_color_string)
        for new_string_point in new_string.stones:
            self._grid[new_string_point] = new_string
        # Reduce liberties of any adjacent strings of the opposite color.
        for other_color_string in adjacent_opposite_color:
            other_color_string.remove_libert(point)
        # If any of the opposite-color strings now have zero liberties, remove them.
        for other_color_string in adjacent_opposite_color:
            if other_color_string.num_liberties == 0:
                self._remove_string(other_color_string)

    def is_on_grid(self, point):
        return 1 <= point.row <= self.num_rows and \
            1 <= point.col <= self.num_cols

    def get(self, point):
        # Returns the content of a point on
        # the board: a Player if a stone is on
        # that point, or else None
        string = self._grid.get(point)
        if string is None:
            return None
        return string.color

    def get_go_string(self, point):
        # Returns the entire string of stones
        # at a point: a GoString if a stone is
        # on that point, or else None
        string = self._grid.get(point)
        if string is None:
            return None
        return string

    def _remove_string(self, string):
        for point in string.stones:
            # removing a string can create liberties for other strings.
            for neighbor in point.neighbors():
                neighbor_string = self._grid.get(neighbor)
                if neighbor_string is None:
                    continue
                if neighbor_string is not string:
                    neighbor_string.add_liberty(point)
            self._grid[point] = None
