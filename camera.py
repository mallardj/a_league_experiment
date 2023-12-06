import numpy as np
from PIL import ImageGrab
import cv2
import time
import win32gui
import pytesseract
import re
import datetime

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'


class LeagueChatEvent():
    def __init__(self, minute, sec, mode, username, champname, msg):
        self.time = datetime.time(minute=minute, second=sec)
        self.mode = mode
        self.username = username
        self.champname = champname
        self.msg = msg


def parse_output(out):
    m = re.match(r"(\d+:\d+)\s*\[\w+]\s*\w+\s*\(\w+\):\s*.+", out)
    parsed_tokens = m.group()
    event = LeagueChatEvent(parsed_tokens)


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


def mask_relevant_colors(src, origsrc):
    mask_white = cv2.inRange(src, (0, 0, 100), (0, 0, 93))
    mask_red = cv2.inRange(src, (0, 80, 100), (0, 80, 93))
    mask_green = cv2.inRange(src, (106.5, 31.3725, 100), (106.5, 31.3725, 93))
    mask_grey = cv2.inRange(src, (0, 0, 82.3529), (0, 0, 75.3529))
    mask_blue = cv2.inRange(src, (199.2265, 74.4856, 95.2941), (199.2265, 74.4856, 88.2941))
    mask_orange = cv2.inRange(src,(38.8235, 100, 100), (38.8235, 100, 93) )
    mask_cyan = cv2.inRange(src, (178.9655, 72.8033, 93.7255), (178.9655, 72.8033, 86))
    masks = [mask_white, mask_red, mask_green, mask_grey, mask_blue, mask_orange, mask_cyan]
    # results = [cv2.bitwise_and(src, src, mask=mask) for mask in masks]
    summed = masks[0]
    for i in masks[1:]:
        summed += i
    final_result = cv2.bitwise_and(origsrc, origsrc, mask=summed)
    return final_result

def camera_capture(dims):
    while True:
        time.sleep(3)  # captures every 5 seconds
        screen_dimensions = dims  # where is that chatbox?
        screen_pil = ImageGrab.grab(screen_dimensions)
        screen_np = np.array(screen_pil)
        screen_hsv = cv2.cvtColor(screen_np, cv2.COLOR_BGR2HSV)
        screen_np = cv2.cvtColor(screen_np, cv2.COLOR_BGR2RGB)
        masked_screen_np = mask_relevant_colors(screen_hsv, screen_np)

        # convert ImageGrab -> CV2: https://stackoverflow.com/questions/32918978/convert-pil-image-to-opencv2-image
        print(pytesseract.image_to_string(masked_screen_np))

        cv2.imshow('window', masked_screen_np)
        if cv2.waitKey(25) & 0xFF == ord('~'):
            cv2.destroyAllWindows()
            break


def start_camera():
    win32gui.EnumWindows(select_window, None)
