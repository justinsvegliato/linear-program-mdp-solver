import math


SLIP_PROBABILITY = 0.1
ACTION_DETAILS = {
    'STAY': {
        'movement': [0, 0],
        'slip_directions': [],
        'is_at_boundary': lambda row, column, grid_world: False,
        'is_valid_move': lambda row, successor_row, column, successor_column: row == successor_row and column == successor_column
    },
    'NORTH': {
        'movement': [-1, 0],
        'slip_directions': ['EAST', 'WEST'],
        'is_at_boundary': lambda row, column, grid_world: row == 0 or grid_world[row - 1][column] == 'W',
        'is_valid_move': lambda row, successor_row, column, successor_column: row == successor_row + 1 and column == successor_column
    },
    'EAST': {
        'movement': [0, 1],
        'slip_directions': ['NORTH', 'SOUTH'],
        'is_at_boundary': lambda row, column, grid_world: column == len(grid_world[row]) - 1 or grid_world[row][column + 1] == 'W',
        'is_valid_move': lambda row, successor_row, column, successor_column: row == successor_row and column == successor_column - 1
    },
    'SOUTH': {
        'movement': [1, 0],
        'slip_directions': ['EAST', 'WEST'],
        'is_at_boundary': lambda row, column, grid_world: row == len(grid_world) - 1 or grid_world[row + 1][column] == 'W',
        'is_valid_move': lambda row, successor_row, column, successor_column: row == successor_row - 1 and column == successor_column
    },
    'WEST': {
        'movement': [0, -1],
        'slip_directions': ['NORTH', 'SOUTH'],
        'is_at_boundary': lambda row, column, grid_world: column == 0 or grid_world[row][column - 1] == 'W',
        'is_valid_move': lambda row, successor_row, column, successor_column: row == successor_row and column == successor_column + 1
    }
}


def get_adjacent_cells(grid_world, row, column, action):
    adjacent_cells = []

    for slip_direction in ACTION_DETAILS[action]['slip_directions']:
        row_offset, column_offset = ACTION_DETAILS[slip_direction]['movement']

        adjacent_row = row + row_offset
        adjacent_column = column + column_offset

        if 0 <= adjacent_row < len(grid_world) and 0 <= adjacent_column < len(grid_world[adjacent_row]):
            adjacent_cell = grid_world[adjacent_row][adjacent_column]
            if adjacent_cell != 'W':
                adjacent_cells.append([adjacent_row, adjacent_column])

    return adjacent_cells


class GridWorldMDP:
    def __init__(self, grid_world):
        self.grid_world = grid_world
        self.width = len(grid_world[0])
        self.height = len(grid_world)

    def states(self):
        return list(range(self.width * self.height))

    def actions(self):
        return list(ACTION_DETAILS.keys())

    def transition_function(self, state, action, successor_state):
        row = math.floor(state / self.width)
        column = state - row * self.width

        successor_row = math.floor(successor_state / self.width)
        successor_column = successor_state - successor_row * self.width

        if self.grid_world[row][column] == 'W':
            if row == successor_row and column == successor_column:
                return 1
            return 0

        adjacent_cells = get_adjacent_cells(self.grid_world, row, column, action)
        for adjacent_cell in adjacent_cells:
            adjacent_row, adjacent_column = adjacent_cell
            if adjacent_row == successor_row and adjacent_column == successor_column:
                return SLIP_PROBABILITY / len(adjacent_cells)

        adjustment = SLIP_PROBABILITY if adjacent_cells else 0

        is_at_boundary = ACTION_DETAILS[action]['is_at_boundary'](row, column, self.grid_world)
        if row == successor_row and column == successor_column and is_at_boundary:
            return 1 - adjustment

        if self.grid_world[successor_row][successor_column] == 'W':
            return 0

        is_valid_move = ACTION_DETAILS[action]['is_valid_move'](row, successor_row, column, successor_column)
        if is_valid_move:
            return 1 - adjustment

        return 0

    def reward_function(self, state, action):
        row = math.floor(state / self.width)
        column = state - row * self.width

        cell = self.grid_world[row][column]

        if cell == 'G' and action == 'STAY':
            return 1

        return 0

    def start_state_function(self, state):
        start_states = []

        for row in range(self.height):
            for column in range(self.width):
                if self.grid_world[row][column] != 'W':
                    start_states.append(self.width * row + column)

        return 1.0 / len(start_states) if state in start_states else 0
