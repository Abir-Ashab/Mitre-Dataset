Here is the new format of each:
system:
  {
    "timestamp": "2025-10-22T06:30:00.872Z",
    "event_type": "system",
    "message": "Network connection detected:\nRuleName: Common Ports\nUtcTime: 2025-10-20 00:44:28.897\nProcessGuid: {ABFC3109-5B72-68F8-8F02-000000002E00}\nProcessId: 11052\nImage: C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe\nUser: DESKTOP-7TQ88T1\\Niloy\nProtocol: udp\nInitiated: true\nSourceIsIpv6: false\nSourceIp: 10.43.0.105\nSourceHostname: DESKTOP-7TQ88T1\nSourcePort: 50487\nSourcePortName: -\nDestinationIsIpv6: false\nDestinationIp: 216.58.200.170\nDestinationHostname: del11s06-in-f10.1e100.net\nDestinationPort: 443\nDestinationPortName: https",
    "winlog": {
      "opcode": "Info",
      "computer_name": "DESKTOP-7TQ88T1",
      "channel": "Microsoft-Windows-Sysmon/Operational",
      "task": "Network connection detected (rule: NetworkConnect)",
      "record_id": 317430,
      "version": 5,
      "event_data": {
        "User": "DESKTOP-7TQ88T1\\Niloy",
        "Initiated": "true",
        "ProcessGuid": "{ABFC3109-5B72-68F8-8F02-000000002E00}",
        "DestinationPortName": "https",
        "SourcePort": "50487",
        "SourceIp": "10.43.0.105",
        "DestinationPort": "443",
        "SourceHostname": "DESKTOP-7TQ88T1",
        "Image": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "DestinationHostname": "del11s06-in-f10.1e100.net",
        "UtcTime": "2025-10-20 00:44:28.897",
        "DestinationIsIpv6": "false",
        "Protocol": "udp",
        "ProcessId": "11052",
        "DestinationIp": "216.58.200.170",
        "RuleName": "Common Ports",
        "SourceIsIpv6": "false",
        "SourcePortName": "-"
      },
      "event_id": "3",
      "provider_name": "Microsoft-Windows-Sysmon",
      "provider_guid": "{5770385F-C22A-43E0-BF4C-06F5698FFBD9}",
      "user": {
        "name": "SYSTEM",
        "identifier": "S-1-5-18",
        "type": "User",
        "domain": "NT AUTHORITY"
      },
      "process": {
        "thread": {
          "id": 2840
        },
        "pid": 4060
      }
    },
    "@version": "1",
    "host": {
      "name": "DESKTOP-7TQ88T1"
    },
    "agent": {
      "ephemeral_id": "85dbddee-7f40-4532-b9de-0c4dc9ec7eb2",
      "id": "ed729226-ba3a-4d44-a977-17ed06c8d3ca",
      "name": "DESKTOP-7TQ88T1",
      "type": "winlogbeat",
      "version": "9.0.2"
    },
    "tags": [
      "beats_input_codec_plain_applied"
    ],
    "event": {
      "original": "Network connection detected:\nRuleName: Common Ports\nUtcTime: 2025-10-20 00:44:28.897\nProcessGuid: {ABFC3109-5B72-68F8-8F02-000000002E00}\nProcessId: 11052\nImage: C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe\nUser: DESKTOP-7TQ88T1\\Niloy\nProtocol: udp\nInitiated: true\nSourceIsIpv6: false\nSourceIp: 10.43.0.105\nSourceHostname: DESKTOP-7TQ88T1\nSourcePort: 50487\nSourcePortName: -\nDestinationIsIpv6: false\nDestinationIp: 216.58.200.170\nDestinationHostname: del11s06-in-f10.1e100.net\nDestinationPort: 443\nDestinationPortName: https",
      "created": "2025-10-22T06:30:01.980Z",
      "kind": "event",
      "provider": "Microsoft-Windows-Sysmon",
      "action": "Network connection detected (rule: NetworkConnect)",
      "code": "3"
    },
    "log": {
      "level": "information"
    },
    "ecs": {
      "version": "8.0.0"
    },
    "host_id": "4c84584a",
    "agent_id": "816d9d59"
  }

network:
  {
    "timestamp": "2025-10-22T06:30:34.409Z",
    "event_type": "network",
    "packet_number": 1,
    "length": 60,
    "summary": "Ether / IP / TCP 52.123.129.14:https > 10.43.0.105:61416 RA / Padding",
    "raw_hex": "f48e38804aef6c3b6bc755df0800450000289b5f40006e06b153347b810e0a2b006901bbefe85e7ea0280f5c7a0f5014000075fd0000000000000000",
    "layers": {
      "Ether": {
        "dst": "f4:8e:38:80:4a:ef",
        "src": "6c:3b:6b:c7:55:df",
        "type": "2048"
      },
      "IP": {
        "version": "4",
        "ihl": "5",
        "tos": "0",
        "len": "40",
        "id": "39775",
        "flags": "DF",
        "frag": "0",
        "ttl": "110",
        "proto": "6",
        "chksum": "45395",
        "src": "52.123.129.14",
        "dst": "10.43.0.105",
        "options": "[]"
      },
      "TCP": {
        "sport": "443",
        "dport": "61416",
        "seq": "1585356840",
        "ack": "257718799",
        "dataofs": "5",
        "reserved": "0",
        "flags": "RA",
        "window": "0",
        "chksum": "30205",
        "urgptr": "0",
        "options": "[]"
      },
      "Padding": {
        "load": "b'\\x00\\x00\\x00\\x00\\x00\\x00'"
      }
    }
  },


  browser:
    {
    "timestamp": "2025-10-22T06:34:18.747Z",
    "event_type": "browser",
    "id": 7453,
    "duration": 5.093,
    "data": {
      "url": "https://chatgpt.com/c/68f86135-88f4-8322-8146-9bf5cd8feefb",
      "title": "Running activity watch as service",
      "audible": false,
      "incognito": false,
      "tabCount": 7
    }
  },
