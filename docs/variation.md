# **MITRE ATT&CK Mapping for Your Attack Steps (Complete Version)**

---

# ✅ **1. Initial Access (By downloading payload)**

**Possible initial entry paths used:**

### **Phishing & Social Engineering**

✔ **T1566.001 – Spearphishing Attachment**
✔ **T1566.002 – Spearphishing Link**
✔ **T1204.001 – Malicious Link Execution** (clicked link triggers download)
✔ **T1598 – Phishing for Information** *(if attacker gathers victim info first)*

### **Download-Based Payload Delivery**

✔ **T1105 – Ingress Tool Transfer** *(any download of malware)*
✔ **T1199 – Trusted Relationship** *(if downloaded from GitHub/Discord where user trusts sender)*
✔ **T1036 – Masquerading** *(payload disguised as legit file)*

### **Malicious File Execution**

✔ **T1204.002 – User Execution: Malicious File**
✔ **T1218 – Signed Binary Proxy Execution** *(e.g., using regsvr32 / rundll32 / mshta)*

### **Archive-Based Payloads**

✔ **T1566.001 + T1204.002** for ZIP/RAR containing malware
✔ **T1027 – Obfuscated/Encrypted Files** *(if payload packed/obfuscated)*

### **USB / Offline Delivery**

✔ **T1091 – Replication through Removable Media**
✔ **T1204.002 – User Execution (USB-executed malware)**

### **Initial Access Blocked / Stopped**

If the payload was prevented from running or killed by defender/attacker:
✔ **T1562.001 – Impair Defenses: Disable Security Tools**
✔ **T1489 – Service Stop**
✔ **T1057 – Process Discovery** *(attacker enumerates and kills processes)*

---

# ✅ **2. Operation After Initial Access**

### **File Tampering / Modification**

✔ **T1070.004 – File Deletion**
✔ **T1565.001 – Stored Data Manipulation**
✔ **T1083 – File System Discovery**
✔ **T1098 – Account Manipulation** *(if victim accounts/data changed)*

---

# ✅ **3. Credential Harvesting**

### **Browser + RAT Tools**

✔ **T1555.003 – Credentials from Web Browsers**
✔ **T1555.004 – Password Managers Extraction** *(if RAT scraped credentials)*
✔ **T1056.001 – Keylogging**
✔ **T1003 – Credential Dumping** (LSASS / SAM)
✔ **T1081 – Credentials in Files** *(if RAT steals saved configs)*

---

# ✅ **4. Attacker Control (Revenge-RAT + Playit.gg)**

### **Command Execution**

✔ **T1059 – Command & Scripting Interpreter**
✔ **T1059.001 – PowerShell** *(if RAT executes PS commands)*
✔ **T1059.003 – Windows Command Shell**

### **C2 Traffic (Revenge-RAT)**

✔ **T1105 – Ingress Tool Transfer**
✔ **T1219 – Remote Access Software**
✔ **T1071.001 – Application Layer Protocol: Web Protocols (HTTPS)**
✔ **T1571 – Non-Standard Port Communication** *(if RAT listens on port 1337)*
✔ **T1090 – Proxy Use (Playit.gg Tunnel)**
✔ **T1572 – Protocol Tunneling** *(Playit forwards TCP → attacker)*

### **Startup Delays / Hidden Execution**

✔ **T1053.005 – Scheduled Task (Delayed Activation)**
✔ **T1546 – Event-Triggered Execution** *(startup triggers, WMI events, etc.)*

---

# ✅ **5. Persistence**

### **Registry / Startup**

✔ **T1547.001 – Registry Run Keys / Startup Folder**
✔ **T1037 – Boot/Logon Initialization Script**
✔ **T1543 – Create/Modify System Process (if RAT installs service)**

### **Advanced Persistence**

✔ **T1053.005 – Scheduled Task Persistence**
✔ **T1546.003 – Windows Management Instrumentation (WMI Event Subscriptions)**

---

# ✅ **6. Data Exfiltration**

### **Physical Media**

✔ **T1048.002 – Exfiltration Over Physical Medium** (USB)

### **Cloud-Based Exfiltration**

✔ **T1567.002 – Exfiltration to Cloud Storage**
(Google Drive, MEGA, OneDrive)

### **C2-Based Exfiltration**

✔ **T1041 – Exfiltration Over Command and Control Channel**
✔ **T1571 – Exfiltration Over Non-Standard Port (1337 → 24547 Tunnel)**

---

# ✅ **7. Final Payload Execution**

### **Ransomware or Data Damage**

✔ **T1486 – Data Encrypted for Impact**
✔ **T1560.001 – Archive Collected Data (7zip)**
✔ **T1490 – Inhibit System Recovery** *(if shadow copies deleted)*
✔ **T1491 – Defacement / Damage to Files**

---

# ✅ **8. Post-Attack Cleanup**

✔ **T1070 – Indicator Removal on Host**
✔ **T1070.004 – File Deletion**
✔ **T1647 – Plist/Registry Cleaning**
✔ **T1074 – Data Staging Removal**
✔ **T1033 – System Owner/Group Discovery** *(to clean specific traces)*

---

# 🔥 **BONUS: MITRE ATT&CK Techniques SPECIFIC to Revenge-RAT + Playit.gg**

Add these anywhere you want:

### **Revenge-RAT Specific**

✔ **T1105 – Ingress Tool Transfer**
✔ **T1219 – Remote Access Software**
✔ **T1056.001 – Keylogging**
✔ **T1113 – Screen Capture**
✔ **T1110 – Brute Force (if RAT tries creds)**
✔ **T1222 – File Permission Modification**

### **Playit.gg Tunneling**

✔ **T1090 – Proxy Use**
✔ **T1572 – Protocol Tunneling**
✔ **T1071 – Application Layer Protocol**
✔ **T1571 – Non-Standard Port (24547)**

---

# 🎁 If you want:

I can generate:

✅ **A full report PDF**
✅ **MITRE heatmap (TIDs highlighted)**
✅ **CSV of all techniques**
✅ **Automatic detection rules (Sigma / YARA / Suricata)**
Just tell me.
