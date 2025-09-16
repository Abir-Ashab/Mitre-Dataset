## **Key Terms**

* **An Advanced Persistent Threat (APT)**  attack is to gain unauthorized access to a network and remain undetected for an extended period to steal sensitive information. It is called persistent because attackers maintain continuous access to the compromised systems by creating multiple backdoors or using advanced evasion techniques. The stages of an APT Attack are:   
  * **Initial Compromise**: Attackers gain entry using phishing, malicious downloads, or exploiting vulnerabilities.  
  * **Establishing a Foothold:** Deploy backdoors or malware to maintain access and communicate with command-and-control (C2) servers.  
  * **Privilege Escalation:** Privilege Escalation consists of techniques adversaries use to gain higher-level permissions on a system or network —When a normal user Elevate/increase/level-up/escalate ‘access privileges’ to administrative levels to gain control over critical systems.   
  * **Lateral Movement:** Move within the network to explore, identify valuable assets, and compromise additional systems.  
  * **Data Exfiltration or Impact:** Steal sensitive data, intellectual property, or cause disruption.  
  * **Maintain Persistence:** Ensure ongoing access even if some vulnerabilities are patched.  
* **Social Engineering** is a manipulation technique that exploits human psychology to gain unauthorized access to systems, networks, or sensitive information. Instead of relying on technical hacking, social engineering attacks exploit human error, trust, or ignorance to achieve the attacker’s objectives. When successful, these attacks often lead to data breaches or ransomware infections.  
* **MITRE ATT\&CK** (Adversarial Tactics, Techniques, and Common Knowledge) is a framework that categorizes and documents real-world attack techniques used by cyber adversaries. Developed by MITRE Corporation, it provides a structured approach for understanding, detecting, and mitigating cyber threats. The framework consists of tactics (attack goals), techniques (methods used), and procedures (specific implementations) used by attackers.  
* **Red Teaming**   
  * A full-scope, adversarial simulation that mimics real-world attacks to test an organization's detection and response capabilities.  
  * Focuses on testing defensive capabilities, response effectiveness, and security controls.  
  * Broad scope, covering people, processes, and technology. It often includes social engineering, physical security breaches, and cyberattacks.  
  * Simulates advanced persistent threats (APTs).  
  * Focuses on achieving real-world objectives (e.g., data exfiltration).

* **Penetration Testing**   
  * A targeted security assessment aimed at identifying and exploiting vulnerabilities in a system, application, or network.  
  * Aims to find and exploit vulnerabilities to assess system security.  
  * Narrow scope, typically limited to specific applications, networks, or systems.  
  * Often follows a checklist-based methodology.  
  * Aims to find as many vulnerabilities as possible.  
      
* **Denial of Service (DoS)** is typically accomplished by flooding the targeted machine or resource with surplus requests in an attempt to overload systems and prevent some or all legitimate requests from being fulfilled. For example, if a bank website can handle 10 people a second by clicking the Login button, an attacker only has to send 10 fake requests per second to make it so no legitimate users can log in  
* **Ransomware** is a type of **malware** that prevents you from accessing your device and the data stored on it, usually by encrypting your files. A criminal group will then demand a ransom in exchange for decryption. The computer itself may become locked, or the data on it might be encrypted, stolen, or deleted.  
  **What Does Ransomware Do?**  
  * Encrypts files: Prevents access to important data.  
  * Locks system functionality: Some variants block users from logging in.  
  * Demands payment: Hackers demand a ransom in exchange for the decryption key.  
  * Spreads across networks: Many ransomware variants infect other systems within the same network.  
  * Deletes backups: To prevent recovery without paying.  
  *   
* **Attack Emulation** is a cybersecurity technique used to mimic real-world cyberattacks in a controlled environment. Its goal is to assess the effectiveness of an organization’s defenses, identify vulnerabilities, and improve overall security posture.  
* **Malware** (short for malicious software) is a category of software designed to harm, exploit, or disrupt systems, networks, and devices. It can steal data, damage files, spy on users, or give attackers unauthorized access to systems.   
* **Cobalt Strike** is a penetration testing toolkit used by ethical hackers and security professionals to simulate real-world cyberattacks.  
* A **Compromised System** refers to a computer, server, or device that has been breached by an attacker, giving them unauthorized access and control.  
* A **C2 System** **(Command-and-Control)** is the infrastructure attackers use to remotely manage and control compromised systems in a cyberattack. It acts as a communication hub between the attacker and the infected devices (often referred to as bots, agents, or implants).  
* A **Beacon** is a lightweight agent (or implant) used in the context of a Command-and-Control (C2) system, specifically in tools like Cobalt Strike. It allows attackers or penetration testers to remotely control a compromised system and execute post-exploitation tasks.  
* **Cloudflare** is a global network of services designed to enhance the security, performance, and reliability of websites, applications, and APIs. It acts as a reverse proxy between the user and a website's server, offering features such as content delivery network (CDN), DDoS protection, web application firewall (WAF), DNS management, and analytics.  
* **Kerberos** is a network authentication protocol designed to provide secure authentication for users and services in a network. It uses symmetric-key cryptography and operates based on tickets to authenticate users and services without transmitting passwords over the network. Tools Used in Kerberos Attacks:  
  * Mimikatz: Extracts Kerberos tickets, hashes, and other credentials.  
  * Rubeus: A C\# tool for Kerberos ticket manipulation and attacks.  
  * Impacket: Python library for network attacks, including Kerberos-related exploits.  
  * Hashcat/John the Ripper: For cracking Kerberos ticket hashes.  
* **AS-REP Roasting and Kerberoasting** These are Kerberos attacks targeting account credentials.  
* **Intrusion** refers to unauthorized access or actions a person or program takes to compromise the confidentiality, integrity, or availability of a system, network, or application.  
* **Sharphound** is a data collection tool used in cybersecurity, specifically for Active Directory (AD) enumeration. Running Sharphound in memory through a Cobalt Strike beacon is an advanced red-teaming technique. Instead of writing the Sharphound executable or script to disk, it is executed directly in memory using the capabilities of the Cobalt Strike beacon. This approach minimizes disk artifacts, making it harder for endpoint detection and response (EDR) or antivirus tools to detect the operation. Attackers use this method to stealthily enumerate Active Directory environments and gather data about relationships, permissions, and potential attack paths without leaving significant traces on the target system.  
* **SMB (Server Message Block)** is a network file-sharing protocol that allows applications or users on a network to access files, printers, and other resources on remote servers.  
* **LSASS (Local Security Authority Subsystem Service)** is a Windows process that enforces security policies on the system. It handles user authentication, password validation, and generating access tokens. LSASS is a critical component of the Windows operating system because it manages sensitive data like user credentials. In cybersecurity, LSASS is often targeted by attackers because it stores credentials in memory. Tools like Mimikatz or attacks like Pass-the-Hash are used to extract credentials or hash values from LSASS, enabling privilege escalation or lateral movement within a network.  
* **RDP (Remote Desktop Protocol)** is a proprietary protocol developed by Microsoft that enables users to connect to and control a remote computer over a network. It allows users to access the graphical desktop of the remote machine as if they were physically present in the system. RDP operates on port **3389** by default and provides features like secure communication, file sharing, clipboard sharing, and device redirection.  
* **Lateral movement** refers to the techniques used by threat actors to navigate through a network after compromising an initial system. Instead of attacking all systems directly, attackers move laterally from one system to another, seeking to escalate privileges, gather data, and achieve their ultimate objective.  
* **Firmware** is embedded software in hardware devices responsible for low-level operations.  
* **An adversary** is a threat actor or attacker attempting to compromise systems or networks.  
* **The attack vector** is a pathway or method a hacker uses to illegally access a network or computer to exploit system vulnerabilities. Hackers use numerous attack vectors to launch attacks that exploit system weaknesses, cause a [data breach](https://www.fortinet.com/resources/cyberglossary/data-breach), or steal [login credentials](https://www.fortinet.com/resources/cyberglossary/login-credentials). Such methods include sharing malware and viruses, malicious email attachments and web links, pop-up windows, and instant messages that involve the attacker duping an employee or individual user.  
* **Metasploit** is one of the best penetration testing frameworks that help businesses discover and shore up their systems' vulnerabilities before exploitation by hackers. To put it simply, Metasploit allows hacking with permission.  
* **Rclone** helps us to backup (and encrypt) files to cloud storage then restore (and decrypt) files from cloud storage.  
* **Mega.io** – A cloud storage service that attackers use to store and exfiltrate stolen data.  
* **FTP exfiltration** means steal data from your network through FTP network.  
* **FTP (File Transfer Protocol)** – A standard network protocol for transferring files, used by attackers for exfiltration.  
* **SystemBC** – A malware that acts as a **proxy tool**, allowing attackers to maintain a persistent, encrypted command-and-control channel on compromised networks.  
* **GhostSOCKS** – Another proxy tool used by attackers to create **encrypted tunnels**, enabling them to evade(avoid) detection while communicating with their C2 servers.  
* **Process Injection** – A technique where malware injects itself into legitimate processes (like `WUAUCLT.exe`) to evade detection and run malicious code.  
* **Credential Dumping (LSASS Process)** – Extracting stored user credentials from `lsass.exe` (Local Security Authority Subsystem Service), a process in Windows responsible for authentication.  
* **Seatbelt & SharpView** – Security assessment tools used to collect system information and Active Directory reconnaissance. Attackers repurpose these tools for lateral movement and privilege escalation.   
* **Scheduled Tasks** – A Windows feature that allows tasks to be scheduled to run at specific times or system events. Attackers use this to automate malware execution.  
* **Registry Run Key** – A method where attackers modify Windows registry entries to execute malware during system startup.  
* **BITSAdmin** – A Windows command-line tool that manages downloads/uploads. Attackers abuse it to download and execute malware.  
* **WMI (Windows Management Instrumentation)** – A Windows feature allowing remote system management. Attackers use it to execute malicious commands remotely.  
* **RDP (Remote Desktop Protocol)** – A protocol used to remotely access Windows systems, often exploited for control over compromised systems.  
* **PsExec** – A legitimate Microsoft tool for executing commands on remote systems, often abused by attackers for lateral movement.  
* **Windows Defender Bypass** – Attackers modify Windows Defender settings (e.g., through Group Policy Editor or Registry) to disable real-time protection, allowing malware to run undetected.  
* **Active Directory Reconnaissance** – Attackers query Active Directory (using nltest) to map out domain controllers, user accounts, and permissions.  
* **Active Directory (AD)**: A directory service used by Windows networks to manage users, computers, and resources centrally.  
* **Domain Controller (DC)**: A server that authenticates and authorizes users and devices in an AD environment. DCs **store and enforce security policies**, manage **logins**, and allow users to access network resources securely.  
* **Network logon** refers to user authentication when accessing network resources (e.g., file servers, applications, or other computers in the domain).  
* **nltest (Net Logon Test)** is a command-line utility in Windows that helps administrators query and diagnose Active Directory (AD) domain controllers and network logon issues. It is commonly used for:  
  * Checking domain controller connectivity  
  * Enumerating trusted domains  
  * Verifying secure channel status  
  * Performing Active Directory reconnaissance (often abused by attackers)  
* **Elevated user permissions** refer to higher-than-normal access rights granted to a user account, allowing it to perform administrative or privileged actions on a system or network. A standard user has limited access and cannot make significant system changes. An elevated user (e.g., an Administrator or Domain Admin) has more control over system operations.  
* **NTDS.dit File** – A sensitive database file on domain controllers that stores hashed passwords for Active Directory users. Attackers attempt to extract this file to gain domain-wide access.  
* **LockBit Ransomware** – A ransomware strain that encrypts files on a victim’s system and demands a ransom in exchange for decryption.  
* **Time to Ransomware (TTR)** – The time taken by an attacker from initial access to deploying ransomware.

