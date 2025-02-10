import cv2
import numpy as np

def dominant_color(image):
    # Find the unique colors and their counts in the image
    colors, count = np.unique(image.reshape(-1, image.shape[-1]), axis=0, return_counts=True)
    # Return the color that appears the most
    return colors[count.argmax()]

def detect_grid(gray):
    # Apply a binary threshold to get a binary image
    _, binary_grid = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)

    # Find contours in the binary image
    contours, _ = cv2.findContours(binary_grid, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

    # Assume the largest contour is the grid
    largest_contour = max(contours, key=cv2.contourArea)

    # Get the bounding box of the largest contour
    x, y, w, h = cv2.boundingRect(largest_contour)

    # Cut the image to the grid
    binary_grid = binary_grid[y:y+h, x:x+w]

    # Initialize the result array
    result = np.ones((8, 8), dtype=int)

    # Calculate the size of each cell
    cell_width = w // 8
    cell_height = h // 8

    # Iterate over each cell in the grid
    for i in range(8):
        for j in range(8):
            # Get the cell region
            cell = binary_grid[i * cell_height:(i + 1) * cell_height, j * cell_width:(j + 1) * cell_width]

            # Check if the cell contains a block
            if cv2.countNonZero(cell) > (cell_width * cell_height) // 2:
                result[i, j] = 0

    # Calculate the bottom of the grid
    bottom_grid = int((y + h) * 1.05)
    return result, bottom_grid, [x, y, w, h]

def adjacent_squares(start_coords, square_coords, dis, piece=None, start_square=None):
    if piece is None or start_square is None:
        start_square = [0, 0, *start_coords]
        piece = [start_square]

    # Define possible directions to move (right, left, down, up, and diagonals)
    directions = [[dis, 0], [-dis, 0], [0, dis], [0, -dis], [dis, dis], [-dis, -dis], [dis, -dis], [-dis, dis]]

    # Function to get the center of a square
    def center(s):
        x, y, w, h, _ = s
        return np.array([x + w//2, y + h//2])

    # Function to check if a coordinate is within a square
    def in_square(c):
        x, y = center(start_coords) + c
        for i, (x2, y2, w2, h2, checked) in enumerate(square_coords):
            if not checked and x >= x2 and x <= x2 + w2 and y >= y2 and y <= y2 + h2:
                square_coords[i][4] = 1   # mark as checked
                return i
        return None

    # Function to add a square to the piece and recursively check adjacent squares
    def add(direction: list, origin_square, next_coords):
        next_square = [*(origin_square[:2] + np.array(direction)/dis), *next_coords]
        piece.append(next_square)
        adjacent_squares(next_coords, square_coords, dis, piece, next_square)

    # Check all possible directions for adjacent squares
    for direction in directions:
        square_index = in_square(direction)
        if square_index is not None:
            add(direction, start_square, square_coords[square_index])

    return piece, square_coords

def squares_to_pieces(squares):
    # Calculate the average distance between squares
    square_spacing = int(np.mean([w + h for _, _, w, h in squares]) / 2)

    coords = np.array(squares).T
    # Sort squares by x and y coordinates
    coords = coords[:, np.lexsort((coords[1, :], coords[0, :]))]

    # Add a checklist column to the coordinates array
    coords = np.concatenate([coords, np.zeros((1, len(coords[0])), dtype=int)])

    coords = coords.T

    complete_pieces = []
    # Loop until all squares are checked
    while not all(coords[:, 4]):
        first_not_checked_square = np.where(coords[:, 4] == 0)[0][0]

        coords[first_not_checked_square][4] = 1    # mark the starting square as checked
        single_piece, coords = adjacent_squares(coords[first_not_checked_square], coords, square_spacing)
        complete_pieces.append(single_piece)
    
    return complete_pieces, square_spacing

def detect_pieces(gray, grid_bottom: int, image=None):
    # Cut image from bottom of grid to the top of the ad
    max_y = int(gray.shape[0]*0.9)
    gray = gray[grid_bottom:max_y, :]

    # Determine the dominant color in the grayscale image and adjust thresholds
    background1 = dominant_color(gray)[0] + 5
    background2 = dominant_color(gray)[0] + 20

    # Create two binary images based on the adjusted thresholds
    gray1 = np.where(gray <= background1, 0, np.maximum(gray + background1, 255))
    gray2 = np.where(gray <= background2, 0, np.maximum(gray + background1, 255))

    # Apply a binary threshold to get binary images
    _, binary1 = cv2.threshold(gray1, 1, 255, cv2.THRESH_BINARY)
    _, binary2 = cv2.threshold(gray2, 1, 255, cv2.THRESH_BINARY)

    # Find contours in the binary images
    contours = cv2.findContours(binary1, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)[0]
    contours += cv2.findContours(binary2, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)[0]

    squares = []
    for contour in contours:
        # Get the bounding box of the contour
        x, y, w, h = cv2.boundingRect(contour)

        # Filter out small contours that are likely noise
        if w > 20 and h > 20 and (w >= h * 0.9 and w <= h * 1.1):
            # Check if the square overlaps with any existing squares
            overlap = False
            for (sx, sy, sw, sh) in squares:
                if x < sx + sw and x + w > sx and y < sy + sh and y + h > sy:
                    overlap = True
                    break
            if not overlap:
                square = gray[y:y+h, x:x+w]
                squares.append((x, y, w, h))

    # Check for no pieces on screen
    if len(squares) == 0:
        return [], [], 0, 0

    # For image cropping, get the bottom of the part where the pieces are displayed
    pieces_bottom = max(squares, key=lambda x: x[1])[1]

    # Get pieces formation from reference point
    instructions, square_spacing = squares_to_pieces(squares)

    pieces, coords = [], []
    # Convert the pieces to a 2D array
    for inst in instructions:
        # Find the top-left corner of the piece
        top = np.min([sub[:2] for sub in inst], axis=0)
        top = np.concatenate([top, np.zeros(len(inst[0])-len(top), dtype=int)])
        
        # Shift the piece coordinates to start from (0, 0)
        shifted = (inst - top).astype(int)
        
        # Find the bottom-right corner of the shifted piece
        bottom = np.max(shifted, axis=0)

        # Initialize an empty array for the piece
        piece = np.zeros(np.flip(bottom[:2] + [1, 1]), dtype=int)
        
        # Fill in the piece array based on the shifted coordinates
        for square in shifted:
            piece[square[1], square[0]] = 1
        
        # Add the piece to the list of pieces
        pieces.append(piece)

        # Calculate the coords of the top left corner and add it to the list
        s = shifted[0]
        # s[2] and s[3] are the original x and y coordinates of the top-left corner of the piece
        # s[0] and s[1] are the shifted x and y coordinates of the top-left corner of the piece
        # distance is the average distance between squares
        # grid_bottom is added so coordinates reference the entire screen
        coords.append([s[2] - s[0] * square_spacing, s[3] - s[1] * square_spacing + grid_bottom])

    return pieces, coords, square_spacing, pieces_bottom + grid_bottom + square_spacing * 2

def detect(image):
    # Check if the image is more than 99% black
    if np.mean(image) < 2.55:
        print("Screen is turned off!")
        exit()

    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect the grid and pieces
    grid, bottom_grid, grid_coords = detect_grid(gray)
    pieces, pieces_coords, square_spacing, pieces_bottom = detect_pieces(gray, bottom_grid)

    area_y = [grid_coords[1] - 3, pieces_bottom]
    return grid, pieces, grid_coords, pieces_coords, square_spacing, area_y