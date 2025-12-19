# **Most Important Sysmon + Windows Security Event Codes (for Attack Detection)**
These are the ones you *must* know while analyzing RAT activity or post-exploitation behavior.

---

# **🟩 Event ID 1 — Process Creation (Sysmon)**

**Meaning:**
A new process started.

**Why important:**
#1 event for detecting malware execution.

**Look for:**

* Suspicious EXEs in Temp/AppData
* Office → cmd.exe → powershell.exe
* RAT payload execution

---

# **🟥 Event ID 3 — Network Connection (Sysmon)**

**Meaning:**
A process created a network connection.

**Why important:**
Critical for detecting **C2 communication**.

**Look for:**

* Connections to foreign IPs
* Ports like 4444, 1337, 8080
* explorer.exe, python.exe, chrome.exe connecting to unknown IPs
* Your RAT contacting 147.185.221.22

---

# **🟦 Event ID 11 — File Create (Sysmon)**

**Meaning:**
A file was created.

**Why important:**
Used for payload drop, RAT modules, screenshots, keystrokes.

---

# **🟧 Event ID 5 — Process Terminate (Sysmon)**

Helps correlate with Event ID 1.
Used to confirm execution timeline.

---

# **🟪 Event ID 7 — Image Loaded (Sysmon)**

**Meaning:**
DLL file loaded into a process.

**Why important:**
Malware loads:

* credential stealing DLLs
* .NET malware assemblies
* Unusual DLLs from Temp/AppData

---

# **🟦 Event ID 10 — Process Access (Sysmon)**

**Meaning:**
Process accessed another process’ memory.

**Why important:**
Used for:

* Credential dumping
* Keylogging
* Token manipulation
* Injection

**Very suspicious.**

---

# **🟫 Event ID 12 — Registry Create/Delete (Sysmon)**

Related to registry structure changes.

---

# **🟨 Event ID 13 — Registry Value Set (Sysmon)**

**Meaning:**
Registry value changed.

**Why important:**
Main method of **persistence**.

Look for keys like:

* `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`
* `HKLM\SYSTEM\CurrentControlSet\Services`

---

# **🟫 Event ID 22 — DNS Query (Sysmon)**

Detects DNS lookups.

Suspicious if querying:

* ngrok.io
* duckdns
* random character domains

---

# **🟥 Event ID 23 — File Delete (Sysmon)**

**Meaning:**
File was deleted.

**Why important:**
Attackers delete logs, payloads, or evidence.
RATs often self-delete.

---

# ✅ **Now Adding the New Windows Security Logs**

These are NOT Sysmon — they’re from the Windows Security Log (Event Viewer → Security).

They matter a LOT for login and access tracking.

---

# **🟩 Event ID 4624 — Successful Logon (Windows Security)**

**Meaning:**
A user or process successfully logged in.

**Why important:**
Shows **every login**, including RAT-driven logins.

**Suspicious indicators:**

* LogonType **3** or **10** (network / remote login)
* TargetUserName = your username (when RAT logged in via API)
* Logon from unusual IP address
* Logon from attacker side

---

# **🟥 Event ID 4672 — Special Privileges Assigned (Windows Security)**

**Meaning:**
An account was given admin privileges (SeDebugPrivilege, etc.)

**Why important:**
Happens when malware obtains elevated rights.

**Suspicious:**

* Appearing right after 4624
* For normal users who don’t have admin
* Used by RATs to dump credentials

---

# **🟦 Event ID 4663 — File Accessed (Windows Security)**

**Meaning:**
A process READ, MODIFIED, or DELETED a file.

**Why important:**
This is how you detect **file upload/download activity**.

**To detect RAT file transfers:**

* Look for many 4663 events involving

  * Desktop
  * Documents
  * Downloads
  * USB drives
  * Sensitive folders
* Look for “ReadData”, “WriteData”, “AppendData”

If the RAT downloaded something **from the victim**, you will see 4663 “ReadData”.
If the RAT uploaded something **to the victim**, you will see 4663 “WriteData”.

---

# **🟥 Event ID 23 (Sysmon) + 4663 (Security) = Full File Deletion Evidence**

Use together to confirm RAT wiping traces.

---

# **🟥 4688 (Security) = **

A new process has been created

---

# **🟥 4689 (Security) = **

A new process has been ended

---

# 🔥 **Updated Top Event IDs for Detecting RATS**

| Source           | Event ID | Why It Matters                 |
| ---------------- | -------- | ------------------------------ |
| Sysmon           | **1**    | Malware execution              |
| Sysmon           | **3**    | C2 connection                  |
| Windows Security | **4624** | Remote login                   |
| Windows Security | **4672** | Privilege escalation           |
| Windows Security | **4663** | File read/write = exfiltration |
| Sysmon           | **11**   | File created (weapon drop)     |
| Sysmon           | **13**   | Persistence registry keys      |
| Sysmon           | **22**   | DNS query to C2                |

---