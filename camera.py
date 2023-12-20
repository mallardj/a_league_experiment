import numpy as np
from PIL import ImageGrab
import cv2
import time
import win32gui
import pytesseract
import re
import datetime
import cassiopeia as cass
from openai import OpenAI

client = OpenAI()

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'


class LeagueChatEvent:
    def __init__(self, game_time, mode, username, champ_name, msg):
        champion_pool = cass.get_champions("NA")
        if champ_name not in champion_pool:
            return
        minute, sec = game_time.split(":")
        self.time = datetime.time(minute=int(minute), second=int(sec))
        self.mode = mode if not (mode is None) else "[Team]"  # OneHotEncode
        self.username = username  # Part of identifier. Do not encode.
        self.champ_name = champ_name  # OneHotEncode
        self.msg = msg  # Embed.
        self.evaluation = self.consultOpenAI()

    def consultOpenAI(self):
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "You perform sentiment analysis on chat dialogue from League of Legends. Where "
                 "-1.0 signifies negative, and 1.0 signifies positive, return a number within [-1.0, 1.0]."
                 "If it's a ping, subtract 0.1 from the total."},
                {"role": "user", "content": self.msg}
            ]
        )
        return sum([float(i.message.content) for i in completion.choices]) / len(completion.choices)

    def __repr__(self):
        return(f"""League Event:
Time: {self.time.__repr__()}
Mode: {self.mode}
Champion: {self.champ_name}
Message: {self.msg}
Evaluation: {self.evaluation}
""")



def parse_output(out):
    regex = r"(?P<time>\d\d:\d\d)\s*(\[[\w ]+\])?\s*([\w ]+)\s*\(([a-zA-Z]+)\):?\s*(.+)"
    ps = re.finditer(regex, out)
    events = []
    for p in ps:
        parsed_tokens = [p.group(i) for i in range(1, 6)]
        event = LeagueChatEvent(*parsed_tokens)
        events.append(event)
    return events


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
    else:
        print("No LoL window detected.")


def mask_relevant_colors(src, origsrc):
    def convert_to_mask(x, value=None):
        if value is None:
            return cv2.inRange(src, (x[0] - 40, x[1] - 40, 100), (x[0] + 40, x[1] + 40, 255))
        else:
            return cv2.inRange(src, (x[0] - 40, x[1] - 40, value - 77), (x[0] + 40, x[1] + 40, 255))

    mask_cyan = (179, 72)
    mask_red = (0, 80)
    mask_green = (106, 31)
    mask_pink = (0, 14)
    mask_blue = (194, 70, 80)
    mask_orange = (38, 100, 130)
    mask_white = (240, 0)
    mask_white2 = (0, 0)

    masks = [mask_white, mask_red, mask_green, mask_blue, mask_orange, mask_cyan, mask_pink, mask_white2]
    results = [convert_to_mask(mask) if len(mask) == 2 else convert_to_mask(mask, mask[2]) for mask in masks]
    final_result = cv2.bitwise_and(origsrc, origsrc, mask=sum(results))

    print(f"Masked Image Shape: {final_result.shape}")
    print(f"Masked Image Max Value: {np.max(final_result)}")
    print(f"Masked Image Min Value: {np.min(final_result)}")
    return final_result


def camera_capture(dims):
    while True:
        time.sleep(3)  # captures every 3 seconds
        screen_dimensions = dims  # where is that chatbox?
        screen_pil = ImageGrab.grab(screen_dimensions)
        screen_np = np.array(screen_pil)
        screen_hsv = cv2.cvtColor(screen_np, cv2.COLOR_BGR2HSV)
        screen_np = cv2.cvtColor(screen_np, cv2.COLOR_BGR2RGB)
        # masked_screen_np = mask_relevant_colors(screen_hsv, screen_np)
        screen_output = pytesseract.image_to_string(screen_np)
        parse_output(screen_output)
        # convert ImageGrab -> CV2: https://stackoverflow.com/questions/32918978/convert-pil-image-to-opencv2-image
        print(pytesseract.image_to_string(screen_np))

        cv2.imshow('window', screen_np)
        if cv2.waitKey(25) & 0xFF == ord('~'):
            cv2.destroyAllWindows()
            break


def start_camera():
    win32gui.EnumWindows(select_window, None)
