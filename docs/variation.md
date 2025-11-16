## Attack Steps 

The `attackSteps` data organizes individual attack choices into categories. Below are the explicit bulleted variants for each category as present in the source data. 

- initialAccess
	- Phishing through email, WhatsApp, Messenger, Telegram that carry or link to malicious executables, compressed archives (zip/rar with or without passwords), files bound into PDFs, payloads delivered via public GitHub repositories (cloning, downloading whole repos, or single files) and physical vectors like USB drop attacks.

- operationAfterInitialAccess
	- Delete/Edit files

- credentialHarvesting
	- RAT + WebBrowserPassView credential extraction

- attackerControl
	- Immediate control after compromise (RAT activation)
	- Delayed control after dormancy period (scheduled activation, trigger-based)

- persistence
	- Bootloader-based payload persistence (using registry)

- dataExfiltration
	- USB exfiltration
	- Google Drive exfiltration
	- RAT server exfiltration
	- OneDrive exfiltration
	- GitHub exfiltration

- finalPayload
	- Ransomware (using 7zip to compress files/folders before encryption)

- postAttackCleanup
	- Leaving traces