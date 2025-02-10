import numpy as np
from gaps import count_gaps

class game:
    def score(grid: np.array, lines:int=None) -> int:
        score = 0
        
        # score for gaps in grid
        segments = count_gaps(grid)
        segments.remove(max(segments))
        
        # lose points for every extra segment
        gap_penalty = len(segments)
        # for each segment having less than 3/4 squares lose points
        gap_penalty += sum(1 for s in segments if s < 3)

        score -= 1 * gap_penalty


        # score for line clearence
        if lines:
            cleared = 2 ** lines -1
            score += 1 * cleared
        return score


    def clear_lines(grid: list) -> list:
        scheduled = []
        cleared_lines = 0

        # rows
        for row in range(len(grid)):
            if np.all(grid[row] == 1):
                scheduled.append(row)
        # columns
        for col in range(len(grid[0])):
            if np.all(grid[:, col] == 1):
                grid[:, col] = np.zeros(8, dtype=int)
                cleared_lines += 1
        
        # clear rows after columns so crosses can be detected
        for row in scheduled:
            grid[row] = np.zeros(8, dtype=int)
            cleared_lines += 1
        
        return grid, game.score(grid, cleared_lines)



def place(grid: list, piece: list, coords: list) -> list:
    # Extract x and y coordinates
    x, y = coords
    # Place the piece on the grid at the specified coordinates
    grid[y:y+piece.shape[0], x:x+piece.shape[1]] += piece
    # Check if any cell in the grid has a value greater than 1 (indicating overlap)
    if np.any(grid > 1):
        return None
    # Return the updated grid
    return grid


def valid_places(grid: list, piece: list) -> list:
    # Initialize a list to store all valid placements
    placings = []
    # Iterate over all possible y coordinates where the piece can be placed
    for y in range(grid.shape[0] - piece.shape[0] + 1):
        # Iterate over all possible x coordinates where the piece can be placed
        for x in range(grid.shape[1] - piece.shape[1] + 1):
            # Place the piece on the grid at the current coordinates
            placed_grid = place(grid.copy(), piece, (x, y))
            # If the placement is valid (no overlap), add it to the list of valid placements
            if placed_grid is not None:
                placings.append([placed_grid, x, y])
    # Return the list of all valid placements
    return placings



def recursive_piece_placement(grid: np.array, pieces: np.array, current_score: int=0, solution=None):
    # create solution list
    if solution is None:
        solution = []

    # if all pieces are placed return the solution and score
    if not pieces:
        return solution, current_score
    
    best_solution = []
    best_score = -100

    # Every piece
    for i, piece in enumerate(pieces):
        remaining_pieces = pieces.copy()
        valid_grids = valid_places(grid, piece)
        remaining_pieces.pop(i)

        # Every possible placement of that piece
        for valid, x, y in valid_grids:
            new_solution = solution + [[i, x, y]]
            cleared, score = game.clear_lines(valid)
            new_score = current_score + score
            
            # Recursively place the remaining pieces
            result, result_score = recursive_piece_placement(cleared, remaining_pieces, new_score, new_solution)
            if result and result_score > best_score:
                best_solution = result
                best_score = result_score
    
    # If every possibility is tested, return the best solution and score
    return best_solution, best_score



def calculate_moves(grid: list, pieces: list):

    empty_score = game.score(grid)
    moves = recursive_piece_placement(grid, pieces)[0]
    return moves