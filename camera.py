import numpy as np
from PIL import ImageGrab
import cv2
import time
import win32gui
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'

def select_window(hwnd, extra):
    # adapted from https://stackoverflow.com/questions/7142342/get-window-position-size-with-python
    if "League of Legends" in win32gui.GetWindowText(hwnd):
        rect = win32gui.GetWindowRect(hwnd)
        x = rect[0]
        y = rect[1]
        w = rect[2] - x
        h = rect[3] - y
        if w > 1 and h > 1 and win32gui.GetWindowText(hwnd) != "":
            print("Window %s:" % win32gui.GetWindowText(hwnd))
            print("\tLocation: (%d, %d)" % (x, y))
            print("\t    Size: (%d, %d)" % (w, h))
        dims = (x + int(w * 15 / 16), y + int(h * 1 / 2), x + (w * 5 / 4), y + int(8 / 11 * h))
        camera_capture(dims)


def camera_capture(dims):
    while True:
        time.sleep(5)  # captures every 5 seconds
        screen_dimensions = dims  # where is that chatbox?
        screen_pil = ImageGrab.grab(screen_dimensions)
        screen_np = np.array(screen_pil.convert('RGB'))
        # convert ImageGrab -> CV2: https://stackoverflow.com/questions/32918978/convert-pil-image-to-opencv2-image

        print(pytesseract.image_to_string(screen_np))

        cv2.imshow('window', screen_np)
        if cv2.waitKey(25) & 0xFF == ord('~'):
            cv2.destroyAllWindows()
            break


def start_camera():
    win32gui.EnumWindows(select_window, None)
