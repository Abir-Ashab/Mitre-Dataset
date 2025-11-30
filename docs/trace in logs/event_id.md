# **Most Important Sysmon Event Codes (for Attack Detection)**

These are the ones you *must* know.

---

# **🟩 Event ID 1 — Process Creation**

**What it means:**
A process started on Windows.

**Why it matters:**
This is the **#1 event** for detecting malware execution.

**What to look for:**

* Suspicious EXEs in Downloads or Temp
* PowerShell, cmd.exe, wscript/cscript
* Untrusted parent → trusted child (e.g., `word.exe` → `cmd.exe`)
* RAT payload execution

**Example:**

```
Crypted.exe was started
```

---

# **🟥 Event ID 3 — Network Connection**

**What it means:**
Process made an outgoing network connection.

**Why it matters (very important):**
Malware communicates with its **C2 server** using this.

**Look for:**

* Connections to IPs on port 4444, 8080, 1337, 5000, etc.
* Unknown foreign IPs
* Chrome.exe or explorer.exe making suspicious connections
* Crypted.exe sending TCP traffic

---

# **🟦 Event ID 11 — File Create**

**What it means:**
A file was created.

**Why it matters:**
Shows:

* Payload downloaded
* Persistence files created
* Data staging
* RAT storing keystrokes/screenshots

**Your logs showed:**
Downloaded `Crypted.exe` and temp files.

---

# **🟧 Event ID 5 — Process Terminate**

**What it means:**
A process ended.

**Why it matters:**
Useful for correlating with Event ID 1 (start).
On its own, not harmful — but helps build the timeline.

**Example:**
`Crypted.exe` terminated → You saw this in your logs.

---

# **🟪 Event ID 7 — Image Loaded (DLL Load)**

**What it means:**
A process loaded a DLL.

**Why it matters:**
Malware often loads:

* Suspicious DLLs
* Credential dumping DLLs
* .NET assemblies for RATs

This is useful for advanced detection.

---

# **🟨 Event ID 13 — Registry Value Set**

**What it means:**
Registry value was changed.

**Why it matters:**
This is **the main way persistence is made**.

Look for:

* `Run` keys
* Services
* Startup folder entries
* RATs often create registry persistence

---

# **🟫 Event ID 22 — DNS Query**

**What it means:**
Process made a DNS lookup.

**Why it matters:**
Malware usually resolves:

* C2 domains
* Dynamic DNS domains

Example suspicious domains:
`ngrok.io`, `duckdns`, random hex strings.

---

# **🟥 Event ID 23 — File Delete**

**What it means:**
A file was marked for deletion.

**Why it matters:**
Attackers delete evidence.

Look for:

* Logs being deleted
* Payload self-delete (common with RATs)

---

# **🟩 Event ID 8 — CreateRemoteThread**

**What it means:**
Process injection attempt.

**Why it matters:**
This is **EXTREMELY suspicious**.
Used for:

* RAT privilege escalation
* Keyloggers
* Injecting into explorer.exe, svchost.exe

---

# **🟦 Event ID 10 — Process Access**

**What it means:**
One process accessed another process’s memory.

**Why it matters:**
Used for:

* Credential dumping
* Keylogging
* Token manipulation

---

# **🟫 Event ID 12 — Registry Object Create/Delete**

Additional registry actions. Not common unless malware is modifying registry structure.

---

# 🔥 The Top 6 Event IDs for Threat Hunting

If you must remember only a few:

| Event ID | Why It's Important            |
| -------- | ----------------------------- |
| **1**    | Malware execution             |
| **3**    | C2 communication              |
| **11**   | Payload drop / file creation  |
| **13**   | Persistence creation          |
| **10**   | Credential access / injection |
| **22**   | DNS queries for C2            |

---
