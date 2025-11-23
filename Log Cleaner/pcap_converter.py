import scapy.all as scapy
import json
import csv
import argparse
from datetime import datetime

def pcap_to_json(pcap_file, json_file):
    """
    Convert PCAP file to JSON format with detailed packet information.
    This preserves all packet data without loss.
    """
    packets = scapy.rdpcap(pcap_file)
    packet_list = []

    for i, pkt in enumerate(packets):
        packet_dict = {
            'packet_number': i + 1,
            'timestamp': float(pkt.time) if hasattr(pkt, 'time') else None,
            'length': len(pkt),
            'summary': pkt.summary(),
            'raw_hex': bytes(pkt).hex(),
            'layers': {}
        }

        # Extract information from each layer
        for layer in pkt.layers():
            layer_name = layer.__name__
            layer_data = {}
            if hasattr(pkt[layer], 'fields'):
                layer_data = pkt[layer].fields
            packet_dict['layers'][layer_name] = layer_data

        packet_list.append(packet_dict)

    with open(json_file, 'w') as f:
        json.dump(packet_list, f, indent=4, default=str)

    print(f"Converted {len(packet_list)} packets to {json_file}")

def pcap_to_csv(pcap_file, csv_file):
    """
    Convert PCAP file to CSV format.
    Note: CSV format is tabular and may not capture all packet details without loss.
    This extracts basic packet information.
    """
    packets = scapy.rdpcap(pcap_file)

    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        # Write header
        writer.writerow(['Packet_Number', 'Timestamp', 'Source_IP', 'Destination_IP',
                        'Source_Port', 'Destination_Port', 'Protocol', 'Length', 'Summary'])

        for i, pkt in enumerate(packets):
            timestamp = float(pkt.time) if hasattr(pkt, 'time') else ''
            src_ip = pkt[scapy.IP].src if scapy.IP in pkt else ''
            dst_ip = pkt[scapy.IP].dst if scapy.IP in pkt else ''
            src_port = pkt[scapy.TCP].sport if scapy.TCP in pkt else (pkt[scapy.UDP].sport if scapy.UDP in pkt else '')
            dst_port = pkt[scapy.TCP].dport if scapy.TCP in pkt else (pkt[scapy.UDP].dport if scapy.UDP in pkt else '')
            protocol = pkt[scapy.IP].proto if scapy.IP in pkt else ''
            length = len(pkt)
            summary = pkt.summary()

            writer.writerow([i+1, timestamp, src_ip, dst_ip, src_port, dst_port, protocol, length, summary])

    print(f"Converted {len(packets)} packets to {csv_file}")

def main():
    parser = argparse.ArgumentParser(description='Convert PCAP file to JSON or CSV')
    parser.add_argument('pcap_file', help='Path to the input PCAP file')
    parser.add_argument('output_file', help='Path to the output file (with .json or .csv extension)')
    parser.add_argument('--format', choices=['json', 'csv'], help='Output format (default: json)', default='json')

    args = parser.parse_args()

    if args.output_file.endswith('.json') or args.format == 'json':
        pcap_to_json(args.pcap_file, args.output_file)
    elif args.output_file.endswith('.csv') or args.format == 'csv':
        pcap_to_csv(args.pcap_file, args.output_file)
    else:
        print("Please specify output format as 'json' or 'csv', or use appropriate file extension")

if __name__ == '__main__':
    main()