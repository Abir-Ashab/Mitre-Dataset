1) For cloning github with payload:
```js
      "label": "suspicious",
      "mitre_techniques": ["T1105", "T1036", "T1027"]
```
2) For executing malicious payload (app.exe) through npm run:
```js
      "label": "suspicious",
      "mitre_techniques": ["T1204.002", "T1199", "T1036"]
```

if process stopped (event_id: 5) then apply:
```js
      "label": "suspicious",
      "mitre_techniques": ["T1489"]
```

3) For 7zip execution, locked and upload:
```js
      "label": "suspicious",
      "mitre_techniques": ["T1486", "T1560.001"]
```

4) for deleting something via 7zip:
```js
      "label": "suspicious",
      "mitre_techniques": ["T1491", "T1070.004"]
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