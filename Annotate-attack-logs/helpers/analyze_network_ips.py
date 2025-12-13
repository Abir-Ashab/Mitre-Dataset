"""
Script to analyze network traffic IPs in annotated log files.
Shows the most common destination IPs to help identify YouTube traffic.
"""
import os
import json
import sys
from collections import Counter


def analyze_network_ips(input_path):
    """Analyze network IPs in the log file."""
    print(f"\nAnalyzing: {os.path.basename(input_path)}")
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logs = data.get('logs', [])
        
        dst_ips = []
        src_ips = []
        
        for log_entry in logs:
            if log_entry.get('event_type') == 'network':
                layers = log_entry.get('layers', {})
                ip_layer = layers.get('IP', {})
                
                dst = ip_layer.get('dst')
                src = ip_layer.get('src')
                
                if dst:
                    dst_ips.append(dst)
                if src:
                    src_ips.append(src)
        
        print(f"\nTotal network packets: {len(dst_ips)}")
        
        # Count destination IPs
        dst_counter = Counter(dst_ips)
        src_counter = Counter(src_ips)
        
        print(f"\n{'='*70}")
        print("Top 20 Destination IPs (most common):")
        print(f"{'='*70}")
        print(f"{'Count':<12} {'IP Address':<20} {'IP Prefix'}")
        print('-'*70)
        
        for ip, count in dst_counter.most_common(20):
            prefix = '.'.join(ip.split('.')[:3]) + '.'
            percentage = (count / len(dst_ips)) * 100
            print(f"{count:<12} {ip:<20} {prefix:<15} ({percentage:.1f}%)")
        
        print(f"\n{'='*70}")
        print("Unique IP prefixes (first 3 octets) - Destination:")
        print(f"{'='*70}")
        
        # Group by prefix
        prefix_counter = Counter()
        for ip in dst_ips:
            prefix = '.'.join(ip.split('.')[:3]) + '.'
            prefix_counter[prefix] += 1
        
        print(f"{'Count':<12} {'Prefix':<20} {'Percentage'}")
        print('-'*70)
        for prefix, count in prefix_counter.most_common(15):
            percentage = (count / len(dst_ips)) * 100
            print(f"{count:<12} {prefix:<20} {percentage:.1f}%")
        
    except Exception as e:
        print(f"ERROR: {e}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_network_ips.py <input_json_file>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    
    if not os.path.exists(input_path):
        print(f"ERROR: File does not exist: {input_path}")
        sys.exit(1)
    
    analyze_network_ips(input_path)


if __name__ == "__main__":
    main()
