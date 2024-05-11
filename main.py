import time
import pyautogui
from mss import mss
import numpy as np
import pygetwindow as gw
import subprocess
import ctypes
import PlayerMovement


def get_process_id_by_name(process_name):

    try:
        pids = subprocess.check_output(
            ['tasklist', '/FI', f'IMAGENAME eq {process_name}', '/FO', 'CSV']).decode().split('\r\n')
        for pid in pids[1:]:
            data = pid.split(',')
            if len(data) > 1:
                return int(data[1].strip('"'))
    except Exception as e:
        print(f"Error finding process: {e}")
    return None



def open_process(pid):

    PROCESS_VM_READ = 0x0010
    return ctypes.windll.kernel32.OpenProcess(PROCESS_VM_READ, False, pid)


# Function to read memory from the specified address in the given process
def read_memory(process_handle, address, num_bytes):

    buffer = ctypes.create_string_buffer(num_bytes)
    bytes_read = ctypes.c_size_t(0)
    if ctypes.windll.kernel32.ReadProcessMemory(process_handle, address, buffer, num_bytes, ctypes.byref(bytes_read)):
        return buffer.raw
    return None


# Screen capture using mss
def capture_screen(region=None):
    with mss() as sct:
        screen = sct.grab(region or sct.monitors[1])
        return np.array(screen)


#playermovement random at the moment
def move_player(action):
    try:
        window = gw.getWindowsWithTitle('mGBA')[0]
        window.activate()
        time.sleep(0.1)
    except IndexError:
        print("mGBA window not found for action.")
        return


    pyautogui.keyDown(action)
    time.sleep(0.01)
    pyautogui.keyUp(action)


# Check for the mGBA window and return its region
def get_mgba_window_region():
    try:
        window = gw.getWindowsWithTitle('mGBA')[0]
        if window:
            window.activate()
            time.sleep(1)
            return {'top': window.top, 'left': window.left, 'width': window.width, 'height': window.height}
        else:
            return None
    except IndexError:
        return None



# Start mGBA with a game
def start_mgba_with_rom(mgba_executable_path, rom_path):
    subprocess.Popen([mgba_executable_path, rom_path])
    time.sleep(5)



def run_ai(process_handle, base_address, trainerID_address):
    while True:
        # Reading X coordinate (2 bytes, unsigned short)
        x_address = base_address + 0x000
        x_pos_data = read_memory(process_handle, x_address, 2)
        x_pos = int.from_bytes(x_pos_data, byteorder='little')

        # Reading Y coordinate (2 bytes, unsigned short)
        y_address = base_address + 0x002
        y_pos_data = read_memory(process_handle, y_address, 2)
        y_pos = int.from_bytes(y_pos_data, byteorder='little')

        # Reading Map Number (1 byte, unsigned char)
        map_number_address = base_address + 0x005
        map_number_data = read_memory(process_handle, map_number_address, 1)
        map_number = int.from_bytes(map_number_data, byteorder='little')

        TrainerID = base_address + 0x000A
        TrainerIDdata = read_memory(process_handle, TrainerID, 2)
        trainernumber = int.from_bytes(TrainerIDdata, byteorder='little')

        print(f"Player X Position: {x_pos}, Player Y Position: {y_pos}, Map Number: {map_number} \nTrainerID: {trainernumber}")


        pyautogui.hold('tab')
        move = np.random.choice(['up', 'down', 'left', 'right', 'x', 'z', 'enter'])
        move_player(move)
        print(move)


        time.sleep(.05)


# Wait for mGBA to launch and start the AI
def wait_for_mgba_and_start():
    print("Waiting for mGBA to launch...")
    process_name = "mGBA.exe"
    pid = get_process_id_by_name(process_name)
    if not pid:
        print("mGBA process not found.")
        return

    process_handle = open_process(pid)
    if not process_handle:
        print("Failed to open process.")
        return

    # Base addresses
    base_address = 0x03005008
    trainerID_address = 0x0300500C

    while True:
        mgba_region = get_mgba_window_region()
        if mgba_region:
            print("mGBA detected. Starting AI...")
            run_ai(process_handle, base_address, trainerID_address)
        else:
            time.sleep(2)


# Paths for mGBA and Game rom
mgba_executable_path = r'C:\Program Files\mGBA\mGBA.exe'
rom_path = 'Pokemon - Leaf Green Version (U) (V1.1).gba'


start_mgba_with_rom(mgba_executable_path, rom_path)
wait_for_mgba_and_start()
