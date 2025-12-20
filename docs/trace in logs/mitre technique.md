1) For cloning github with payload/downloading payload from any:
```js
      "label": "suspicious",
      "mitre_techniques": ["T1566.001", "T1105", "T1036", "T1027"]
```
2) For executing malicious payload (app.exe) through npm run (event_id: 1):
```js
      "label": "suspicious",
      "mitre_techniques": ["T1204.002", "T1199", "T1036"]
```

if process stopped (event_id: 5) then apply:
```js
      "label": "suspicious",
      "mitre_techniques": ["T1489"]
```

if process create (event_id: 11) then apply:
```js
      "label": "suspicious",
      "mitre_techniques": [ "T1105", "T1036.007"]
```

if process create (event_id: 4688 (security, not sysmon)) then apply:
```js
      "label": "suspicious",
      "mitre_techniques": [
        "T1204.002",
        "T1036.007", 
        "T1566.001" 
      ]
```

if process stopped (event_id: 4689 (security, not sysmon)) then apply:
```js
      "label": "suspicious",
      "mitre_techniques": [
        "T1027.002"
      ]
```
if special privilege given (event_id: 4672 (security, not sysmon)) then apply:
```js
      "label": "suspicious",
      "mitre_techniques": [
         "T1134.001",
         "T1055",
         "T1003.001"
      ]
```

if special privilege given (event_id: 4703 (security, not sysmon)) then apply:
```js
      "label": "suspicious",
      "mitre_techniques": [
         "T1134.001"
      ]
```

For network connection (event_ id: 3):
```js
      "label": "suspicious",
      "mitre_techniques": ["T1071"]
```

For network connection by dns query(event_ id: 22):
```js
      "label": "suspicious",
      "mitre_techniques": ["T1071.004"]
```

3) For 7zip execution, locked and upload:
```js
      "label": "suspicious",
      "mitre_techniques": ["T1486", "T1560.001"]
```

4) for deleting something via 7zip:
(event_id : 23)
```js
      "label": "suspicious",
      "mitre_techniques": ["T1491", "T1070.004"]
```

(event_id : 26)
```js
      "label": "suspicious",
      "mitre_techniques": ["T1070"]
```

5) for uploading warning file/photo via 7zip:
```js
      "label": "suspicious",
      "mitre_techniques": ["T1105"]
```

6) for webpass viewer (credential harvesting):
```js
      "label": "suspicious",
      "mitre_techniques": [
        "T1555.003",
        "T1555.004"
      ]
```

7) for deleting something normally:
```js
      "label": "suspicious",
      "mitre_techniques": ["T1485"]
```

9) If a process created a new .bat file in Temp.:
```js
      "label": "suspicious",
      "mitre_techniques": ["T1105"]
```

10) For executing via cmd a bat file:
```js
      "label": "suspicious",
      "mitre_techniques": ["T1059.003"]
```

11) For c2 connection:
```js
      "label": "suspicious",
      "mitre_techniques": ["T1571", "T1071.001", "T1090", "T1572"]
```

12) Replication through removable media (pen-drive)
```js
      "label": "suspicious",
      "mitre_techniques": ["T1091"]
```

13) For adding logon autostart using registry:
```js
      "label": "suspicious",
      "mitre_techniques": ["T1547.001", "T1059.003", "T1112"]
```

14) Deleting malicious file by RAT after execution: (Event-id: 23)
```js
      "label": "suspicious",
      "mitre_techniques": ["T1070.004", "T1562.001", "T1027"]
```

15) Keylogging/capturing/writing activity to the victim device (RAT default)
```js
      "label": "suspicious",
      "mitre_techniques": ["T1056.001", "T1119", "T1074.001"]
```