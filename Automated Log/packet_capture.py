import subprocess
import os
import time
import sys
import re
from datetime import datetime
import ctypes
from upload_to_gdrive import upload_file_from_path

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

def is_wifi_interface(interface_line):
    """Check if an interface is likely a WiFi interface based on name patterns."""
    # Convert to lowercase for case-insensitive matching
    interface_lower = interface_line.lower()
    
    # Common WiFi interface indicators
    wifi_indicators = [
        'wi-fi', 'wifi', 'wireless', 'wlan', 'wlp', 'ww', 'wg',
        'wireless network adapter', 'wireless lan', 'wireless-ac',
        'wireless-n', 'wireless-g', 'wireless adapter', 'wi-fi adapter'
    ]
    
    return any(indicator in interface_lower for indicator in wifi_indicators)

def is_ethernet_interface(interface_line):
    """Check if an interface is likely an Ethernet interface based on name patterns."""
    # Convert to lowercase for case-insensitive matching
    interface_lower = interface_line.lower()
    
    # Common Ethernet interface indicators
    ethernet_indicators = [
        'ethernet', 'eth', 'enp', 'ens', 'eno', 'lan', 'local area connection',
        'realtek', 'intel ethernet', 'broadcom netxtreme', 'marvell yukon',
        'family controller', 'gigabit', 'fast ethernet', 'network adapter'
    ]
    
    # Exclude WiFi interfaces that might contain some ethernet keywords
    if is_wifi_interface(interface_line):
        return False
    
    return any(indicator in interface_lower for indicator in ethernet_indicators)

def get_preferred_interface():
    """Automatically select the best available network interface (WiFi first, then Ethernet)."""
    interfaces = get_network_interfaces()
    
    wifi_interfaces = []
    ethernet_interfaces = []
    
    print("Analyzing available network interfaces...")
    for i, interface in enumerate(interfaces, 1):
        print(f"{i}. {interface}")
        
        if is_wifi_interface(interface):
            wifi_interfaces.append((i, interface))
            print(f"   → Detected as WiFi interface")
        elif is_ethernet_interface(interface):
            ethernet_interfaces.append((i, interface))
            print(f"   → Detected as Ethernet interface")
    
    # Prioritize WiFi interfaces first
    if wifi_interfaces:
        selected = wifi_interfaces[0]  # Take the first WiFi interface
        print(f"\n✓ Selected WiFi interface: {selected[1]}")
        return str(selected[0])
    
    # Fall back to Ethernet interfaces
    elif ethernet_interfaces:
        selected = ethernet_interfaces[0]  # Take the first Ethernet interface
        print(f"\n✓ Selected Ethernet interface: {selected[1]}")
        return str(selected[0])
    
    # If no WiFi or Ethernet found, show all interfaces and let user choose
    else:
        print("\n⚠ No WiFi or Ethernet interfaces automatically detected.")
        print("Available interfaces:")
        for i, interface in enumerate(interfaces, 1):
            print(f"{i}. {interface}")
        
        try:
            choice = int(input("Please manually select interface number: "))
            if 1 <= choice <= len(interfaces):
                return str(choice)
            else:
                print("Invalid interface number")
                sys.exit(1)
        except ValueError:
            print("Invalid input. Please enter a number.")
            sys.exit(1)

def get_env_or_fail(var):
    value = os.environ.get(var)
    if value is None:
        print(f"Environment variable '{var}' is required but not set.")
        sys.exit(1)
    return value

def capture_packets(interface, folder_id, timestamp, duration=None):
    """Capture packets using tshark for the specified duration and upload to Google Drive."""
    
    # Create temporary directory for local capture
    temp_dir = "temp_captures"
    os.makedirs(temp_dir, exist_ok=True)
    temp_file = os.path.join(temp_dir, f"packet_capture_{timestamp}.pcap")
    
    if duration is None:
        duration = int(get_env_or_fail("PACKET_CAPTURE_DURATION_MINUTES")) * 60
    tshark_cmd = [
        'tshark',
        '-i', interface,
        '-a', f'duration:{duration}',
        '-w', temp_file
    ]
    
    print(f"Starting capture for {duration} seconds on interface: {interface}")
    print(f"Temporary file: {temp_file}")
    print("Capture in progress... (this will take some time)")
    
    try:
        # Don't capture output so we can see tshark's progress
        result = subprocess.run(tshark_cmd, check=True)
        print(f"Local capture completed: {temp_file}")
        
        # Check if file was created and has content
        if os.path.exists(temp_file):
            file_size = os.path.getsize(temp_file)
            print(f"File size: {file_size} bytes")
            if file_size > 0:
                print("✓ Packet capture successful!")
                
                # Upload to Google Drive
                filename = f"packet_capture_{timestamp}.pcap"
                upload_file_from_path(temp_file, folder_id, filename)
                
                # Clean up temporary file
                os.remove(temp_file)
                print(f"Uploaded and cleaned up: {filename}")
                return filename
            else:
                print("⚠ Warning: Capture file is empty - no packets captured")
                os.remove(temp_file)
                return None
        
        return None
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
            folder_id = sys.argv[1]  # Now Google Drive folder ID
            timestamp = sys.argv[2]
            
            # Upload error message to Google Drive
            from upload_to_gdrive import upload_file_from_content
            error_content = f"""PACKET CAPTURE FAILED
Reason: Administrator privileges required
Attempted at: {datetime.now()}
Solution: Run the main script as Administrator
"""
            filename = f"packet_capture_error_{timestamp}.txt"
            upload_file_from_content(error_content, folder_id, filename, 'text/plain')
            print(f"Error uploaded to Google Drive: {filename}")
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
    
    if len(sys.argv) > 2:
        folder_id = sys.argv[1]  # Google Drive folder ID
        timestamp = sys.argv[2]
        
        # Automatically detect and select the best interface
        interface_num = get_preferred_interface()
        capture_packets(interface_num, folder_id, timestamp)
    else:
        # Interactive mode - automatically detect and select interface
        interface_num = get_preferred_interface()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        capture_packets(interface_num, "packet_captures", timestamp)