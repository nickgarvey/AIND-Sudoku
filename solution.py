import itertools

# diagonality is implemented by adding two units, see diagonal_units
ENABLE_DIAGONAL = True

assignments = []

rows = 'ABCDEFGHI'
cols = '123456789'

def cross(a, b):
    return [s+t for s in a for t in b]

boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
diagonal_units = [[''.join(b) for b in zip(rows, cols)],
                  [''.join(b) for b in zip(rows, reversed(cols))]]

unitlist = row_units + column_units + square_units \
        + (diagonal_units if ENABLE_DIAGONAL else [])

units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def non_duplicate_pairs(lst):
    for i in range(len(lst)):
        for j in range(i + 1, len(lst)):
            yield lst[i], lst[j]

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    for boxes in unitlist:
        # find naked twins
        twins = [(first, second)
                 for first, second in non_duplicate_pairs(boxes)
                 if (len(values[first]) == 2 or len(values[second]) == 2)
                 and values[first] == values[second]]
        # do elimination
        for first, second in twins:
            for box in boxes:
                if box in [first, second]:
                    continue
                for digit in values[first]:
                    values[box] = values[box].replace(digit, '')
    return values

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    return dict(zip(boxes, (c if c != '.' else '123456789' for c in grid)))

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    assert len(values) == 9 * 9
    for i in range(9):
        print(values[(9 * i):(9 * i + 9)])

def eliminate(values):
    for box in boxes:
        if len(values[box]) == 1:
            for peer in peers[box]:
                values[peer] = values[peer].replace(values[box], '')
    return values

def only_choice(values):
    for unit in unitlist:
        for digit in '123456789':
            boxes_with_digit = [box for box in unit if digit in values[box]]
            if len(boxes_with_digit) == 1:
                values[boxes_with_digit[0]] = digit
    return values

def reduce_puzzle(values):
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        eliminate(values)
        only_choice(values)
        naked_twins(values)

        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if any(box for box in values.keys() if not box):
            return False
    return values

def search(values):
    "Using depth-first search and propagation, create a search tree and solve the sudoku."
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if not values:
        return False
    elif all(len(v) == 1 for v in values.values()):
        return values

    # Choose one of the unfilled squares with the fewest possibilities
    square_to_guess = min(
        values.keys(),
        key=lambda k: len(values[k]) if len(values[k]) != 1 else 0xFFFFFF
    )

    for guess in values[square_to_guess]:
        values_with_guess = values.copy()
        values_with_guess[square_to_guess] = guess
        result = search(values_with_guess)
        if result:
            return result
    return False

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    return search(grid_values(grid))

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
