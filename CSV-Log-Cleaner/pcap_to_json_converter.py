"""Convert PCAP/PCAPNG files to JSON format matching log_parser.py logic."""
import sys
import json
from datetime import datetime, timezone


def parse_pcap_to_json(pcap_path, output_file=None):
    """
    Parse PCAP file using Scapy to preserve all packet data.
    Follows the same logic as log_parser.py's parse_pcap_logs function.
    """
    try:
        import scapy.all as scapy
    except ImportError:
        print("Error: Scapy not installed. Install with: pip install scapy")
        return []
    
    print("=" * 60)
    print("PCAP to JSON Converter")
    print("=" * 60)
    print(f"\nInput file: {pcap_path}")
    
    # Determine output file
    if not output_file:
        output_file = pcap_path.replace('.pcap', '_converted.json').replace('.pcapng', '_converted.json')
    print(f"Output file: {output_file}")
    
    events = []
    
    try:
        print("\n=== Reading PCAP file with Scapy ===")
        packets = scapy.rdpcap(pcap_path)
        print(f"Total packets: {len(packets)}")
        
        print("\n=== Processing Packets ===")
        for i, pkt in enumerate(packets):
            raw_timestamp = float(pkt.time) if hasattr(pkt, 'time') else None
            timestamp = None
            
            if raw_timestamp:
                try:
                    dt = datetime.fromtimestamp(raw_timestamp, tz=timezone.utc)
                    timestamp = dt.isoformat(timespec='milliseconds').replace('+00:00', 'Z')
                except Exception as e:
                    print(f"Network log timestamp error for packet {i+1}: {str(e)}")
                    timestamp = None
            
            # Preserve all packet data
            event = {
                'timestamp': timestamp,
                'event_type': 'network',
                'packet_number': i + 1,
                'length': len(pkt),
                'summary': pkt.summary(),
                'raw_hex': "",
                'layers': {}
            }
            
            # Extract information from each layer
            for layer in pkt.layers():
                layer_name = layer.__name__
                layer_data = {}
                if hasattr(pkt[layer], 'fields'):
                    for field_name, field_value in pkt[layer].fields.items():
                        if hasattr(field_value, '__str__'):
                            layer_data[field_name] = str(field_value)
                        else:
                            layer_data[field_name] = field_value
                event['layers'][layer_name] = layer_data
            
            events.append(event)
            
            # Progress indicator
            if (i + 1) % 1000 == 0:
                print(f"  Processed {i + 1} packets...")
        
        print(f"\nParsed {len(events)} network packets")
        
    except Exception as e:
        print(f"Error parsing PCAP with Scapy: {e}")
        import traceback
        traceback.print_exc()
        return []
    
    # Write to output file (JSONL format - one JSON object per line)
    print("\n=== Writing Output ===")
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for event in events:
                f.write(json.dumps(event, ensure_ascii=False) + '\n')
        print(f"Successfully wrote {len(events)} packets to {output_file}")
    except Exception as e:
        print(f"Error writing output: {e}")
        return []
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Total packets:   {len(events)}")
    print(f"Output format:   JSONL (one JSON per line)")
    print(f"Output file:     {output_file}")
    print("=" * 60)
    
    return events


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pcap_to_json_converter.py <pcap_file> [output_file]")
        print("\nArguments:")
        print("  pcap_file   : Path to the PCAP/PCAPNG file to convert")
        print("  output_file : (Optional) Output JSON file path (default: input_converted.json)")
        print("\nExamples:")
        print('  python pcap_to_json_converter.py "traffic.pcap"')
        print('  python pcap_to_json_converter.py "traffic.pcapng" "output.json"')
        sys.exit(1)
    
    pcap_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        parse_pcap_to_json(pcap_file, output_file)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
