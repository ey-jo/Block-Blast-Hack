# pieces are scaled to the grid, x=x and y = w/2 at bottom of grid
import numpy as np

class control:
    def __init__(self, device, coords, square_spacing, speed:int=None):
        self.device = device
        # Set the spacing between squares
        self.spacing = square_spacing
        # Unpack the coordinates
        x, y, w, h = coords
        # Create a grid of coordinates
        self.grid = np.array([[[round(x + w/8*i), round(y + h/8*j)] for i in range(8)] for j in range(8)])
        # Set the bottom coordinate
        self.bottom = y + h
        # Scaling from piece to grid size
        self.scale = round(((w+h)/16) / self.spacing, 2)

        # Adjustment factor for piece movement
        self.adjust = 0.73
        # Duration for the swipe action
        self.duration = speed or 500

    def move_piece(self, start:list, dest: list):
        # Unpack start and destination coordinates
        x1, y1 = start
        x2, y2 = dest

        # Calculate the difference in x and y coordinates
        diff_x = int((x1 - x2) * self.adjust)
        diff_y = int((y1 - y2) * self.adjust)
        
        # Adjust the destination coordinates
        x2 = x1 - diff_x
        y2 = y1 - diff_y

        # Perform the swipe action on the device
        self.device.shell(f"input swipe {x1} {y1} {x2} {y2} {self.duration}")

    def get_center(self, piece, piece_coords):
        # Get center coordinates and scale the piece to grid size
        # Transform to get height and width right
        return piece_coords + np.array(piece.T.shape) * (self.spacing / 2)

    def destination(self, move, start, center):
        """
        Calculate where to set the destination to move the piece to the actual destination
        """
        # Print out the destination of the piece
        print(f"Shape {move[0]} to {move[1:]}")
        move = move[1:]

        # Scale the piece relative to the center
        corner = center - (center - start) * self.scale
        # Piece is moved up so center y matches bottom of grid
        corner[1] += self.bottom - center[1]

        # Get the destination coordinates from the grid using the move indices
        dest = self.grid[*move[::-1]]

        # Apply piece offset
        return start + dest - corner

    def schedule(self, pieces, pieces_coords, moves):
        # Iterate over each move in the moves list
        for i, move in enumerate(moves):
            # Order of pieces to be placed
            index = move[0] + i

            # Getting center of piece
            center = self.get_center(pieces.copy()[index], pieces_coords[index])
            
            # Getting start position for drag action
            start = pieces_coords[index]

            # Getting destination of piece
            dest = self.destination(move, start, center)

            # Move the piece from start to destination
            self.move_piece(start, dest)