"""
Network event analyzer for EventID 3 (Sysmon) and 5156 (Windows Security).

Analyzes network connection events for C2 beaconing, data exfiltration, etc.
Based on real attack traces from user's documentation.
"""

from typing import Dict, Any, List
from analyzers.base_analyzer import BaseAnalyzer
from models.analysis_result import EventAnalysis, SeverityLevel
from rules import suspicious_patterns, normal_patterns


class NetworkAnalyzer(BaseAnalyzer):
    """Analyzes network connection events."""
    
    # Event IDs this analyzer handles
    SUPPORTED_EVENT_IDS = [3, 5156, 5157]
    
    def can_analyze(self, event: Dict[str, Any]) -> bool:
        """Check if event is a network connection event."""
        event_id = self.get_field_value(event, 'event_id')
        if not event_id:
            event_id = self.get_field_value(event, 'EventID')
        
        try:
            return int(event_id) in self.SUPPORTED_EVENT_IDS
        except (ValueError, TypeError):
            return False
    
    def analyze(self, event: Dict[str, Any]) -> EventAnalysis:
        """Analyze network connection event."""
        # Extract event metadata
        event_id = self.get_field_value(event, 'event_id',
                                       self.get_field_value(event, 'EventID', 'Unknown'))
        timestamp = self.extract_timestamp(event)
        
        # Extract network details - try both Sysmon and Security log formats
        dest_ip = self.get_field_value(event, 'DestinationIp',
                                      self.get_field_value(event, 'DestAddress', ''))
        dest_port = self.get_field_value(event, 'DestinationPort',
                                        self.get_field_value(event, 'DestPort', 0))
        src_ip = self.get_field_value(event, 'SourceIp',
                                     self.get_field_value(event, 'SourceAddress', ''))
        src_port = self.get_field_value(event, 'SourcePort', 0)
        
        # Process information
        image = self.get_field_value(event, 'Image',
                                    self.get_field_value(event, 'Application', ''))
        process_name = image.split('\\')[-1].lower() if image else 'unknown'
        
        # Protocol information
        protocol = self.get_field_value(event, 'Protocol', '')
        
        # Packet details (from pcap/network logs)
        tcp_flags = self.get_field_value(event, 'tcp_flags', '')
        packet_size = self.get_field_value(event, 'packet_size', 0)
        raw_load = self.get_field_value(event, 'raw_load', '')
        
        # Analyze for suspicious patterns
        indicators = []
        field_references = []
        mitre_techniques = []
        severity = SeverityLevel.LOW
        analysis_text = ""
        
        # Check if internal communication
        is_internal = normal_patterns.is_internal_ip(dest_ip)
        
        if not is_internal or packet_size or tcp_flags:  # Analyze external traffic or detailed packet data
            # Check for C2 beaconing (from user's RevengeRAT traces)
            c2_indicators = self._check_c2_beaconing(dest_ip, dest_port, tcp_flags, packet_size)
            if c2_indicators:
                indicators.extend(c2_indicators)
                field_references.append(f"DestinationIp={dest_ip}")
                field_references.append(f"DestinationPort={dest_port}")
                if tcp_flags:
                    field_references.append(f"tcp_flags={tcp_flags}")
                if packet_size:
                    field_references.append(f"packet_size={packet_size}")
                mitre_techniques.extend(['T1071.001', 'T1095'])  # Web Protocols, Non-Application Layer Protocol
                severity = max(severity, SeverityLevel.CRITICAL)
            
            # Check for malware download (from user's download traces)
            download_indicators = self._check_malware_download(tcp_flags, packet_size, raw_load)
            if download_indicators:
                indicators.extend(download_indicators)
                field_references.append(f"tcp_flags={tcp_flags}")
                field_references.append(f"packet_size={packet_size}")
                mitre_techniques.extend(['T1105'])  # Ingress Tool Transfer
                severity = max(severity, SeverityLevel.HIGH)
            
            # Check high-risk ports
            if dest_port:
                try:
                    port_info = suspicious_patterns.get_port_risk_info(int(dest_port))
                    if port_info:
                        indicators.append(f"Connection to high-risk port: {port_info['description']}")
                        field_references.append(f"DestinationPort={dest_port}")
                        mitre_techniques.extend(port_info['techniques'])
                        severity = max(severity, SeverityLevel.MEDIUM)
                except (ValueError, TypeError):
                    pass  # Skip if port is invalid
            
            # Check suspicious process making connection
            if process_name in suspicious_patterns.SUSPICIOUS_PROCESSES:
                info = suspicious_patterns.SUSPICIOUS_PROCESSES[process_name]
                indicators.append(f"Network connection by suspicious process: {info['description']}")
                field_references.append(f"Image={image}")
                mitre_techniques.extend(info['techniques'])
                severity = max(severity, SeverityLevel.HIGH)
            
            # Check known malicious IPs
            is_malicious, reason = suspicious_patterns.is_suspicious_ip(dest_ip)
            if is_malicious:
                indicators.append(f"Connection to known malicious IP: {dest_ip} ({reason})")
                field_references.append(f"DestinationIp={dest_ip}")
                mitre_techniques.append('T1071')
                severity = max(severity, SeverityLevel.CRITICAL)
            
            # Build analysis text
            if indicators:
                direction = f"{src_ip}:{src_port} → {dest_ip}:{dest_port}"
                analysis_text = f"Network connection by {process_name}: {direction}. "
                analysis_text += " | ".join(indicators)
            else:
                # Check if standard port
                is_standard, port_desc = normal_patterns.is_standard_port(int(dest_port) if dest_port else 0)
                if is_standard:
                    analysis_text = f"Normal {port_desc} traffic from {process_name} to {dest_ip}:{dest_port}"
                    field_references.append(f"DestinationPort={dest_port}")
                else:
                    analysis_text = f"Network connection from {process_name} to {dest_ip}:{dest_port}"
        else:
            # Internal communication
            analysis_text = f"Internal network communication from {process_name} to {dest_ip}:{dest_port}"
            field_references.append(f"DestinationIp={dest_ip}")
        
        return EventAnalysis(
            event_id=str(event_id),
            event_type='Network',
            timestamp=timestamp,
            analysis_text=analysis_text,
            indicators=indicators,
            severity=severity,
            field_references=field_references,
            mitre_techniques=list(set(mitre_techniques))
        )
    
    def _check_c2_beaconing(self, dest_ip: str, dest_port: Any, tcp_flags: str, packet_size: Any) -> List[str]:
        """
        Check for C2 beaconing patterns based on user's RevengeRAT traces.
        
        Patterns from c2 server trace.md:
        - Small periodic packets (54 bytes)
        - ACK-only flags
        - External IP (147.185.221.22, 150.171.27.10 in traces)
        - Consistent port
        
        Args:
            dest_ip: Destination IP
            dest_port: Destination port
            tcp_flags: TCP flags
            packet_size: Packet size in bytes
            
        Returns:
            List of C2 indicators
        """
        indicators = []
        
        # Check small periodic packets
        if packet_size and suspicious_patterns.C2_INDICATORS['small_periodic_packets']['min_size'] <= int(packet_size) <= suspicious_patterns.C2_INDICATORS['small_periodic_packets']['max_size']:
            indicators.append(f"Small periodic packet ({packet_size} bytes) - typical C2 beaconing pattern")
        
        # Check ACK-only keepalive
        if tcp_flags and 'A' in tcp_flags and len(tcp_flags) <= 2:  # ACK or ACK+FIN only
            if not packet_size or int(packet_size) < 100:
                indicators.append("ACK-only small packet - C2 keepalive beaconing")
        
        # Check external IP beaconing
        if dest_ip and not normal_patterns.is_internal_ip(dest_ip):
            if packet_size and int(packet_size) < 100:
                indicators.append(f"External IP beaconing to {dest_ip} - potential C2 server")
        
        return indicators
    
    def _check_malware_download(self, tcp_flags: str, packet_size: Any, raw_load: str) -> List[str]:
        """
        Check for malware download patterns based on user's download traces.
        
        Patterns from download_trace.md:
        - PSH+ACK flags
        - Large packets (>500 bytes)
        - Non-zero Raw.load payloads
        - Server to client direction
        
        Args:
            tcp_flags: TCP flags
            packet_size: Packet size
            raw_load: Raw payload data
            
        Returns:
            List of download indicators
        """
        indicators = []
        
        # Check PSH+ACK with large payload
        if tcp_flags and 'P' in tcp_flags and 'A' in tcp_flags:
            if packet_size and int(packet_size) > suspicious_patterns.C2_INDICATORS['malware_download']['min_packet_size']:
                indicators.append(f"PSH+ACK with large payload ({packet_size} bytes) - potential file download")
        
        # Check non-zero raw load
        if raw_load and len(raw_load) > 0:
            if packet_size and int(packet_size) > 500:
                indicators.append("Non-empty TCP payload with large packet - potential malware download")
        
        return indicators
