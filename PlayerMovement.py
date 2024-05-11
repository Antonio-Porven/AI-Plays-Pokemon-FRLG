import time
import pyautogui
from mss import mss
import numpy as np
import pygetwindow as gw
import subprocess
import ctypes


def move_player(action):
    try:
        window = gw.getWindowsWithTitle('mGBA')[0]
        window.activate()
        time.sleep(0.1)  # Ensure the window is ready
    except IndexError:
        print("mGBA window not found for action.")
        return

    # Simulate a longer key press
    pyautogui.keyDown(action)
    time.sleep(0.01)  # Hold the key for 0.1 seconds
    pyautogui.keyUp(action)