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

def run_script(script_name, output_folder, timestamp, *args):
    """Run a Python script as a subprocess."""
    cmd = ["python", script_name, output_folder, timestamp]
    cmd.extend(args)
    process = subprocess.Popen(cmd)
    processes.append(process)
    return process

def stop_all_processes():
    """Stop and clear all running subprocesses."""
    for process in processes:
        try:
            process.terminate()
            process.wait(timeout=5)
        except:
            process.kill()
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

    base_output_dir = get_env_or_fail("BASE_OUTPUT_DIR")
    os.makedirs(base_output_dir, exist_ok=True)

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
            output_folder = os.path.join(base_output_dir, timestamp)
            os.makedirs(output_folder, exist_ok=True)

            print(f"New interval started at {interval_start}, saving to {output_folder}")

            print(" -> Starting screen recording...")
            run_script(SCREEN_RECORDING_SCRIPT, output_folder, timestamp)

            print(" -> Starting packet capture...")
            run_script(PACKET_CAPTURE_SCRIPT, output_folder, timestamp, "4")

            time.sleep(INTERVAL_MINUTES * 60)

            print(f"\nInterval ended ({INTERVAL_MINUTES} mins). Stopping processes...")
            stop_all_processes()

            print(" -> Extracting system logs for this interval...")
            run_script(LOG_EXTRACTION_SCRIPT, output_folder, timestamp)

            print(" -> Extracting browser logs for this interval...")
            run_script(BROWSER_LOG_SCRIPT, output_folder, timestamp, str(INTERVAL_MINUTES))

            for process in processes:
                process.wait()
            processes.clear()

            print("Ready for next interval...\n")
    finally:
        clock_process.terminate()
        clock_process.wait()

if __name__ == "__main__":
    main()