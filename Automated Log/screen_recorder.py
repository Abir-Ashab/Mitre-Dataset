import cv2
import numpy as np
import win32gui
import win32ui
import win32con
import time
import os
from datetime import datetime
import sys

def get_actual_screen_size():
    hdesktop = win32gui.GetDesktopWindow()
    left, top, right, bottom = win32gui.GetWindowRect(hdesktop)
    width = right - left
    height = bottom - top
    return width, height


def get_env_or_fail(var):
    value = os.environ.get(var)
    if value is None:
        print(f"Environment variable '{var}' is required but not set.")
        sys.exit(1)
    return value

def screen_capture(output_folder, timestamp):
    screen_width = int(get_env_or_fail("SCREEN_WIDTH"))
    screen_height = int(get_env_or_fail("SCREEN_HEIGHT"))
    fps = float(get_env_or_fail("SCREEN_FPS"))
    segment_duration = int(get_env_or_fail("SCREEN_SEGMENT_DURATION_MINUTES")) * 60

    os.makedirs(output_folder, exist_ok=True)
    output_file = os.path.join(output_folder, f"screen_record_{timestamp}.avi")
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_file, fourcc, fps, (screen_width, screen_height))

    hdesktop = win32gui.GetDesktopWindow()
    desktop_dc = win32gui.GetWindowDC(hdesktop)
    dc_obj = win32ui.CreateDCFromHandle(desktop_dc)
    cdc = dc_obj.CreateCompatibleDC()
    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(dc_obj, screen_width, screen_height)
    cdc.SelectObject(bmp)

    total_frames = int(fps * segment_duration)
    frame_count = 0

    print(f"Recording started: {output_file}")

    while frame_count < total_frames:
        loop_start = time.time()

        cdc.BitBlt((0, 0), (screen_width, screen_height), dc_obj, (0, 0), win32con.SRCCOPY)
        bmp_str = bmp.GetBitmapBits(True)
        img = np.frombuffer(bmp_str, dtype='uint8')
        img.shape = (screen_height, screen_width, 4)

        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        out.write(img)
        frame_count += 1

        elapsed = time.time() - loop_start
        delay = max(0, (1 / fps) - elapsed)
        time.sleep(delay)

    out.release()
    win32gui.DeleteObject(bmp.GetHandle())
    cdc.DeleteDC()
    dc_obj.DeleteDC()
    win32gui.ReleaseDC(hdesktop, desktop_dc)

    print(f"Saved recording: {output_file}")

if __name__ == "__main__":
    try:
        if len(sys.argv) > 2:
            output_folder = sys.argv[1]
            timestamp = sys.argv[2]
            screen_capture(output_folder, timestamp)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_folder = get_env_or_fail("SCREEN_RECORDINGS_DIR")
            screen_capture(default_folder, timestamp)
    except KeyboardInterrupt:
        print("Screen recording stopped by user")