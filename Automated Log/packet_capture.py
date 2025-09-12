import subprocess
import os
import time
import sys
import re
from datetime import datetime
import ctypes

def is_admin():
    """Check if the script is running with administrator privileges on Windows."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_network_interfaces():
    """List available network interfaces using tshark."""
    try:
        result = subprocess.run(['tshark', '-D'], capture_output=True, text=True, check=True)
        interfaces = result.stdout.splitlines()
        return interfaces
    except subprocess.CalledProcessError as e:
        print(f"Error listing interfaces: {e}")
        sys.exit(1)

def get_env_or_fail(var):
    value = os.environ.get(var)
    if value is None:
        print(f"Environment variable '{var}' is required but not set.")
        sys.exit(1)
    return value

def capture_packets(interface, output_folder, timestamp, duration=None):
    """Capture packets using tshark for the specified duration and save with provided timestamp."""
    os.makedirs(output_folder, exist_ok=True)
    output_file = os.path.join(output_folder, f"packet_capture_{timestamp}.pcap")
    if duration is None:
        duration = int(get_env_or_fail("PACKET_CAPTURE_DURATION_MINUTES")) * 60
    tshark_cmd = [
        'tshark',
        '-i', interface,
        '-a', f'duration:{duration}',
        '-w', output_file
    ]
    
    print(f"Starting capture for {duration} seconds on interface: {interface}")
    print(f"Output file: {output_file}")
    print("Capture in progress... (this will take some time)")
    
    try:
        # Don't capture output so we can see tshark's progress
        result = subprocess.run(tshark_cmd, check=True)
        print(f"Saved packet capture: {output_file}")
        
        # Check if file was created and has content
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"File size: {file_size} bytes")
            if file_size > 0:
                print("✓ Packet capture successful!")
            else:
                print("⚠ Warning: Capture file is empty - no packets captured")
        
        return output_file
    except subprocess.CalledProcessError as e:
        print(f"Error during packet capture: {e}")
        print("Possible issues:")
        print("1. Interface name might be incorrect")
        print("2. Insufficient privileges (run as Administrator)")
        print("3. Interface might not be active")
        print("4. No network traffic during capture period")
        return None
    except KeyboardInterrupt:
        print("Packet capture stopped by user")
        return None

def parse_interface_name(full_line):
    """Extract just the interface name from tshark -D output"""
    # For Windows, tshark expects the device path, not the friendly name
    # Format: "1. \Device\NPF_{GUID} (Interface Name)"
    # We need to extract the \Device\NPF_... part
    
    parts = full_line.split(' ', 1)
    if len(parts) > 1:
        device_and_name = parts[1]
        # Extract the device path - look for pattern before the space and parentheses
        # Split at the space before the parentheses to get the device path
        device_parts = device_and_name.split(' (')
        if len(device_parts) > 0:
            device_path = device_parts[0]
            if device_path.startswith('\\Device\\NPF_') or device_path == 'etwdump':
                return device_path
    
    # Fallback - return the whole line minus the number
    return full_line.split(' ', 1)[1] if ' ' in full_line else full_line

if __name__ == "__main__":
    # Check for admin privileges first
    if not is_admin():
        print("ERROR: Packet capture requires administrator privileges.")
        
        # If called from main.py with arguments, create an error file instead of exiting
        if len(sys.argv) > 3:
            output_folder = sys.argv[1]
            timestamp = sys.argv[2]
            os.makedirs(output_folder, exist_ok=True)
            error_file = os.path.join(output_folder, f"packet_capture_error_{timestamp}.txt")
            with open(error_file, 'w') as f:
                f.write("PACKET CAPTURE FAILED\n")
                f.write("Reason: Administrator privileges required\n")
                f.write(f"Attempted at: {datetime.now()}\n")
                f.write("Solution: Run the main script as Administrator\n")
            print(f"Error logged to: {error_file}")
            sys.exit(1)
        else:
            print("Please run PowerShell or Command Prompt as Administrator and try again.")
            print("\nTo run as administrator:")
            print("1. Right-click on PowerShell/Command Prompt")
            print("2. Select 'Run as administrator'")
            print("3. Navigate to this folder and run the script again")
            print("\nAlternatively, try this command in an admin PowerShell:")
            print(f"Start-Process python -ArgumentList '{os.path.abspath(__file__)}' -Verb runAs")
            sys.exit(1)
    
    if len(sys.argv) > 3:
        output_folder = sys.argv[1]
        timestamp = sys.argv[2]
        interface_num = sys.argv[3]
        interfaces = get_network_interfaces()
        # Use the interface number directly instead of parsing device path
        capture_packets(interface_num, output_folder, timestamp)
    else:
        interfaces = get_network_interfaces()
        print("Available network interfaces:")
        for i, iface in enumerate(interfaces, 1):
            print(f"{i}. {iface}")
        try:
            choice = int(input("Select interface number (e.g., 1): "))
            if 1 <= choice <= len(interfaces):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                # Use the interface number directly
                capture_packets(str(choice), "packet_captures", timestamp)
            else:
                print("Invalid interface number")
                sys.exit(1)
        except ValueError:
            print("Invalid input. Please enter a number.")
            sys.exit(1)