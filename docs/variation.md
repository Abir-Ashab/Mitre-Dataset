# **MITRE ATT&CK Mapping for Your Attack Steps**

## **1. Initial Access (By downloading payload)**

**Techniques involved:**

* **Phishing (Email / Messaging Apps):**
  ✔ **T1566.001 – Spearphishing Attachment**
  ✔ **T1566.002 – Spearphishing Link**

* **Malicious files (ZIP/RAR/PDF with embedded payloads):**
  ✔ **T1204.002 – User Execution: Malicious File**

* **GitHub-based payload delivery (clone/download repo or file):**
  ✔ **T1105 – Ingress Tool Transfer**

* **USB Drop Attack:**
  ✔ **T1091 – Replication Through Removable Media**
  ✔ **T1204.002 – User Execution: Malicious File**

---

## **2. Operation After Initial Access**

* **Deleting or editing files:**
  ✔ **T1070.004 – File Deletion**
  ✔ **T1098 – Account Manipulation** *(if modifying config/auth files)*
  ✔ **T1565.001 – Stored Data Manipulation**

---

## **3. Credential Harvesting**

* **RAT + WebBrowserPassView:**
  ✔ **T1555.003 – Credentials from Web Browsers**
  ✔ **T1056 – Input Capture** *(if RAT logs keystrokes)*
  ✔ **T1003 – Credential Dumping**

---

## **4. Attacker Control**

* **Immediate RAT control:**
  ✔ **T1059 – Command and Scripting Interpreter**
  ✔ **T1105 – Ingress Tool Transfer**
  ✔ **T1219 – Remote Access Software**

* **Delayed / scheduled activation:**
  ✔ **T1053.005 – Scheduled Task/Job: Scheduled Task**
  ✔ **T1546 – Event Triggered Execution**

---

## **5. Persistence**

* **Bootloader-based payload persistence via registry:**
  ✔ **T1547.001 – Boot or Logon Autostart Execution: Registry Run Keys / Startup Folder**
  ✔ **T1037 – Boot or Logon Initialization Scripts**

---

## **6. Data Exfiltration**

* **USB drive:**
  ✔ **T1048.002 – Exfiltration Over Physical Medium**

* **Google Drive / OneDrive:**
  ✔ **T1567.002 – Exfiltration to Cloud Storage**

* **RAT server:**
  ✔ **T1041 – Exfiltration Over Command and Control Channel**

---

## **7. Final Payload**

* **Ransomware (compression before encryption):**
  ✔ **T1486 – Data Encrypted for Impact**
  ✔ **T1560.001 – Archive via Utility (7zip)**

---

## **8. Post-Attack Cleanup**

* **Leaving traces / clearing traces:**
  ✔ **T1070 – Indicator Removal on Host**
  ✔ **T1070.004 – File Deletion**
  ✔ **T1647 – Plist/Registry Cleaning** *(if registry cleanup)*

---

