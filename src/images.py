import os
import cv2

def get_images(pattern=None):
    paths = ["images/" + f for f in os.listdir('images') if f.endswith('.png')]
    for path in paths:
        if not pattern:
            yield cv2.imread(path)
        elif pattern in path:
            yield cv2.imread(path)


if __name__ == "__main__":
    print(get_images())