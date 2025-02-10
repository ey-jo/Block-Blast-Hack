from numpy import array_equal

from images import get_images
from src import capture
from src.detect import detect
from src.play import calculate_moves
from src.touch import control


class screen:
    def __init__(self, device, area: list):
        self.device = device
        self.top, self.bottom = area

    def await_change(self, current_frame) -> None:
        # capturing an image using adb takes about a second, all effects to disappear about 0.25 seconds
        img1 = current_frame[self.top:self.bottom, :]
        img2 = capture.screenshot(self.device)[self.top:self.bottom, :]
        # Loop until the screen changes
        while not array_equal(img1, img2):
            img1 = img2
            img2 = capture.screenshot(self.device)[self.top:self.bottom, :]
        

def listing(l: list, header: str) -> None:
    # Print the header and list elements with their indices
    print(header)
    for i, element in enumerate(l):
        print(i, element)
    print()


def main(image, device=None, input_controller=None, delay_handler=None):
    # Detect grid, pieces, and other parameters from the image
    grid, pieces, grid_coords, pieces_coords, square_spacing, area = detect(image)

    # Debug mode: calculate moves without interacting with the device
    if not device:
        moves = calculate_moves(grid, pieces)
        return

    # No piece is detected
    if not pieces:
        print("No pieces detected")
        delay_handler.await_change(image)
    # More than 3 pieces are detected
    elif len(pieces) > 3:
        print("Too many pieces detected")
        listing(pieces, "Pieces:")
        delay_handler.await_change(image)
    else:
        listing(pieces, "Pieces:")
        moves = calculate_moves(grid, pieces)
        # No moves calculated
        if not moves:
            raise ValueError("No moves available")
        # More moves than pieces calculated
        elif len(moves) > len(pieces):
            raise ValueError("Too many moves calculated.")
        # Everything as intended
        else:
            # listing(moves, "Moves:")
            if not input_controller or not delay_handler:
                delay_handler = screen(device, area)
                input_controller = control(device, grid_coords, square_spacing)
            input_controller.schedule(pieces, pieces_coords, moves)
            return input_controller, delay_handler


if __name__ == "__main__":
    debug = False

    if debug:
        for image in get_images("z3"):
            main(image)
            input("Press Enter to continue...")
    else:
        phone = capture.setup()
        image = capture.screenshot(phone)
        controller, delay_handler = main(image, phone)
        
        # Main loop to continuously capture screenshots and process them
        while True:
            image = capture.screenshot(phone)
            main(image, phone, controller, delay_handler)
            print("Continuing...")
            delay_handler.await_change(image)