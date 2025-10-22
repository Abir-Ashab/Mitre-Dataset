import os
from dotenv import load_dotenv
load_dotenv()
import subprocess
import time
from datetime import datetime, timedelta
import threading
import signal
import sys
import ctypes
from upload_to_gdrive import get_main_folder_id, create_folder

def is_admin():
    """Check if the script is running with administrator privileges on Windows."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_env_or_fail(var):
    value = os.environ.get(var)
    if value is None:
        print(f"Environment variable '{var}' is required but not set.")
        sys.exit(1)
    return value

INTERVAL_MINUTES = int(get_env_or_fail("INTERVAL_MINUTES"))
SCREEN_RECORDING_SCRIPT = get_env_or_fail("SCREEN_RECORDING_SCRIPT")
PACKET_CAPTURE_SCRIPT = get_env_or_fail("PACKET_CAPTURE_SCRIPT")
LOG_EXTRACTION_SCRIPT = get_env_or_fail("LOG_EXTRACTION_SCRIPT")
BROWSER_LOG_SCRIPT = get_env_or_fail("BROWSER_LOG_SCRIPT")

processes = []
stop_event = threading.Event()

def run_script(script_name, folder_id, timestamp, *args):
    """Run a Python script as a subprocess with Google Drive folder ID."""
    cmd = ["python", script_name, folder_id, timestamp]
    cmd.extend(args)
    process = subprocess.Popen(cmd)
    processes.append(process)
    return process

def stop_all_processes():
    """Stop and clear all running subprocesses gracefully."""
    for process in processes:
        try:
            if process.poll() is None:  # Process is still running
                print(f"Waiting for process to complete naturally...")
                process.wait(timeout=10)  # Wait up to 10 seconds
        except subprocess.TimeoutExpired:
            print(f"Process taking too long, terminating...")
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print(f"Process unresponsive, killing...")
                process.kill()
        except Exception as e:
            print(f"Error stopping process: {e}")
    processes.clear()

def signal_handler(sig, frame):
    """Graceful shutdown on Ctrl+C."""
    print("\nShutting down monitoring system...")
    stop_event.set()
    stop_all_processes()
    sys.exit(0)

def main():
    # Check for admin privileges for packet capture
    if not is_admin():
        print("WARNING: This script is not running with administrator privileges.")
        print("Packet capture will fail and only create error files.")
        print("\nTo enable packet capture:")
        print("1. Right-click on PowerShell/Command Prompt")
        print("2. Select 'Run as administrator'")
        print("3. Navigate to this folder and run: python main.py")
        print("\nContinuing with monitoring (packet capture will be skipped)...")
        print("-" * 60)

    signal.signal(signal.SIGINT, signal_handler)

    # Initialize Google Drive and create main folder
    print("Initializing Google Drive connection...")
    main_folder_id = get_main_folder_id()
    print(f"Main folder created/found in Google Drive")

    print("Starting continuous monitoring system...")
    print(f"Interval: {INTERVAL_MINUTES} minutes\n")

    print(" -> Starting always-on-top clock...")
    clock_process = subprocess.Popen([sys.executable, "clock.py"])

    try:
        while not stop_event.is_set():
            interval_start = datetime.now().replace(second=0, microsecond=0)
            print(f"Monitor Interval starting at {interval_start}")
            timestamp = interval_start.strftime("%Y%m%d_%H%M%S")
            print(f"Timestamp for this interval: {timestamp}")
            
            # Create timestamp folder in Google Drive
            timestamp_folder_id = create_folder(timestamp, main_folder_id)
            print(f"Created folder in Google Drive for timestamp: {timestamp}")

            print(f"New interval started at {interval_start}, uploading to Google Drive folder: {timestamp}")

            print(" -> Starting screen recording...")
            run_script(SCREEN_RECORDING_SCRIPT, timestamp_folder_id, timestamp)

            print(" -> Starting packet capture...")
            run_script(PACKET_CAPTURE_SCRIPT, timestamp_folder_id, timestamp)

            time.sleep(INTERVAL_MINUTES * 60)

            print(f"\nInterval ended ({INTERVAL_MINUTES} mins). Waiting for processes to complete...")
            
            # Wait for all background processes (screen recording and packet capture) to complete
            for process in processes:
                if process.poll() is None:  # Process is still running
                    print(f"Waiting for process to complete...")
                    process.wait()

            print(" -> Extracting system logs for this interval...")
            run_script(LOG_EXTRACTION_SCRIPT, timestamp_folder_id, timestamp)

            print(" -> Extracting browser logs for this interval...")
            run_script(BROWSER_LOG_SCRIPT, timestamp_folder_id, timestamp, str(INTERVAL_MINUTES))

            # Wait for log extraction processes to complete
            for process in processes[-2:]:  # Only wait for the last 2 processes (log extraction)
                process.wait()
            processes.clear()

            print("Ready for next interval...\n")
    finally:
        clock_process.terminate()
        clock_process.wait()

if __name__ == "__main__":
    main()