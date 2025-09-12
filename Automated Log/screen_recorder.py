import cv2
import numpy as np
import win32gui
import win32ui
import win32con
import time
import os
import gc
from datetime import datetime
import sys
from upload_to_gdrive import upload_file_from_path

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

def screen_capture(folder_id, timestamp):
    screen_width = int(get_env_or_fail("SCREEN_WIDTH"))
    screen_height = int(get_env_or_fail("SCREEN_HEIGHT"))
    fps = float(get_env_or_fail("SCREEN_FPS"))
    segment_duration = int(get_env_or_fail("SCREEN_SEGMENT_DURATION_MINUTES")) * 60

    # Check actual screen size and adjust if needed
    actual_width, actual_height = get_actual_screen_size()
    if actual_width < screen_width or actual_height < screen_height:
        print(f"Warning: Configured resolution {screen_width}x{screen_height} exceeds actual screen {actual_width}x{actual_height}")
        screen_width = min(screen_width, actual_width)
        screen_height = min(screen_height, actual_height)
        print(f"Adjusted to: {screen_width}x{screen_height}")

    # Create temporary local file
    temp_dir = "temp_recordings"
    os.makedirs(temp_dir, exist_ok=True)
    temp_file = os.path.join(temp_dir, f"screen_record_{timestamp}.avi")
    
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(temp_file, fourcc, fps, (screen_width, screen_height))

    # Initialize Windows GDI objects
    hdesktop = None
    desktop_dc = None
    dc_obj = None
    cdc = None
    bmp = None
    
    try:
        hdesktop = win32gui.GetDesktopWindow()
        desktop_dc = win32gui.GetWindowDC(hdesktop)
        dc_obj = win32ui.CreateDCFromHandle(desktop_dc)
        cdc = dc_obj.CreateCompatibleDC()
        bmp = win32ui.CreateBitmap()
        bmp.CreateCompatibleBitmap(dc_obj, screen_width, screen_height)
        cdc.SelectObject(bmp)

        total_frames = int(fps * segment_duration)
        frame_count = 0

        print(f"Recording started: {temp_file}")

        while frame_count < total_frames:
            loop_start = time.time()

            try:
                cdc.BitBlt((0, 0), (screen_width, screen_height), dc_obj, (0, 0), win32con.SRCCOPY)
                
                # Get bitmap bits correctly
                bmp_str = bmp.GetBitmapBits(True)  # True returns raw bytes data
                
                if bmp_str:
                    img = np.frombuffer(bmp_str, dtype='uint8')
                    
                    # Calculate expected size and reshape accordingly
                    expected_size = screen_height * screen_width * 4
                    if len(img) >= expected_size:
                        img = img[:expected_size]  # Truncate if larger
                        img.shape = (screen_height, screen_width, 4)
                        
                        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                        out.write(img)
                        frame_count += 1
                    else:
                        print(f"Warning: Bitmap data size mismatch. Expected {expected_size}, got {len(img)}")
                        frame_count += 1  # Skip this frame but continue
                        
                    # Clear the bitmap string from memory immediately
                    del bmp_str
                    del img
                    
                else:
                    print("Warning: Failed to get bitmap data")
                    frame_count += 1  # Skip this frame but continue
                    
            except MemoryError as e:
                print(f"Memory error at frame {frame_count}: {e}")
                print("Attempting to continue with reduced quality...")
                frame_count += 1  # Skip this frame but continue
            except Exception as e:
                print(f"Error capturing frame {frame_count}: {e}")
                frame_count += 1  # Skip this frame but continue

            elapsed = time.time() - loop_start
            delay = max(0, (1 / fps) - elapsed)
            time.sleep(delay)
            
            # Force garbage collection every 30 frames to free memory
            if frame_count % 30 == 0:
                gc.collect()

    finally:
        # Clean up resources in proper order
        if out is not None:
            out.release()
        if bmp is not None:
            win32gui.DeleteObject(bmp.GetHandle())
        if cdc is not None:
            cdc.DeleteDC()
        if dc_obj is not None:
            dc_obj.DeleteDC()
        if desktop_dc is not None and hdesktop is not None:
            win32gui.ReleaseDC(hdesktop, desktop_dc)

    print(f"Local recording completed: {temp_file}")
    
    # Upload to Google Drive
    filename = f"screen_record_{timestamp}.avi"
    upload_file_from_path(temp_file, folder_id, filename)
    
    # Clean up temporary file
    os.remove(temp_file)
    print(f"Uploaded and cleaned up: {filename}")

if __name__ == "__main__":
    try:
        if len(sys.argv) > 2:
            folder_id = sys.argv[1]  # Now receiving Google Drive folder ID
            timestamp = sys.argv[2]
            screen_capture(folder_id, timestamp)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # For standalone use - you'll need to provide folder_id
            print("Error: This script now requires a Google Drive folder ID")
            print("Run from main.py for proper integration")
            sys.exit(1)
    except KeyboardInterrupt:
        print("Screen recording stopped by user")