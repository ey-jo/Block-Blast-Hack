from ppadb.client import Client as AdbClient
import cv2

def setup():
    # Initialize the ADB client with default host and port
    client = AdbClient(host="127.0.0.1", port=5037)
    
    # Get the list of connected devices
    devices = client.devices()
    
    # Check if there are no devices connected
    if len(devices) == 0:
        print("No device connected")
        exit()
    
    # Get the first connected device
    device = client.device(devices[0].serial)
    return device

def screenshot(device):
    # Capture the screen of the device
    result = device.screencap()
    
    # Save the screenshot to a file
    with open("screen.png", "wb") as fp:
        fp.write(result)
        
        # Read the image file using OpenCV
        img = cv2.imread("screen.png")
        return img