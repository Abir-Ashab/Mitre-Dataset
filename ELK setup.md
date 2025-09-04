Setting up the ELK Stack (Elasticsearch, Logstash, Kibana) on a Windows system to observe Windows logs for security threats involves several steps. The process includes installing the core ELK components and configuring a log shipper like Winlogbeat to collect and send Windows event logs to the stack for analysis. Below is a step-by-step guide to help you install and configure the ELK Stack on a Windows Server (e.g., Windows Server 2019 or later) for monitoring security threats. This guide assumes you are starting from scratch and focuses on a basic setup suitable for security log analysis.

### **Step-by-Step Installation Guide**

#### **Step 1: Install Elasticsearch**
1. **Download and Extract**:
   - Download the Elasticsearch ZIP file from [Elastic downloads](https://www.elastic.co/downloads/elasticsearch) (e.g., `elasticsearch-8.17.2-windows-x86_64.zip`).
   - Extract it to `E:\Hacking\ELK Stack` and rename the folder to `elasticsearch` for simplicity (e.g., `E:\Hacking\ELK Stack\elasticsearch`).

2. **Configure Elasticsearch**:
   - Open `E:\Hacking\ELK Stack\elasticsearch\config\elasticsearch.yml` in a text editor.
   - Add or modify the following basic settings:
     ```yaml
     cluster.name: elk-security
     node.name: node-1
     network.host: 127.0.0.1
     http.port: 9200
     xpack.security.enabled: true
     ```
   - Save the file.

3. **Install Elasticsearch as a Service**:
   - Open PowerShell as Administrator and navigate to the Elasticsearch bin directory:
     ```powershell
     cd "E:\Hacking\ELK Stack\elasticsearch-9.0.2\bin"
     ```
   - Run the service installation script:
     ```powershell
     .\elasticsearch-service.bat install
     ```
   - Start the service:
     ```powershell
     .\elasticsearch-service.bat start
     ```
   - Get the password:
     ```powershell
      .\elasticsearch-reset-password.bat -u elastic
     ```
     - Example output: `Password for the elastic user: Cd8FuiCptd0mJlNGQSZJ`.

4. **Verify Elasticsearch**:
   - Open a browser and navigate to `http://localhost:9200`.
   - When prompted, enter the username `elastic` and the password from the previous step.
   - You should see a JSON response with cluster details, confirming Elasticsearch is running.

#### **Step 2: Install Kibana**
1. **Download and Extract**:
   - Download the Kibana ZIP file from [Elastic downloads](https://www.elastic.co/downloads/kibana) (e.g., `kibana-8.17.2-windows-x86_64.zip`).
   - Extract it to `E:\Hacking\ELK Stack` and rename the folder to `kibana` (e.g., `E:\Hacking\ELK Stack\kibana`).

2. **Configure Kibana**:
   - Open `E:\Hacking\ELK Stack\kibana\config\kibana.yml` in a text editor.
   - Add or modify the following settings:
     ```yaml
      server.port: 5601
      server.host: "127.0.0.1"
      
      elasticsearch.hosts: ["http://localhost:9200"]
      # elasticsearch.username: "elastic"
      # elasticsearch.password: "rvrveOxs5wrmyI9Ld0hV"
      
      # Use service account token instead
      elasticsearch.serviceAccountToken: "AAEAAWVsYXN0aWMva2liYW5hL2tpYmFuYS10b2tlbjpnVF9FS0tzeFRkaUQ5cDBoVTEtQkRn"
      
      # Encryption keys (replace with your own generated keys)
      xpack.encryptedSavedObjects.encryptionKey: 50efe4f8b8bb7208a04a35b6fffb7d3b
      xpack.reporting.encryptionKey: b4d79a09e9e00c78e4de198c6e2305ab
      xpack.security.encryptionKey: b2a64a1396097cce56e95901646cea3e
      
      # Optional: Increase logging
      logging.root.level: info
     ```
     By default there is no username, password. So no worries.

3. **Start Kibana**:
   - In PowerShell, navigate to the Kibana bin directory:
     ```powershell
     cd E:\Hacking\ELK Stack\kibana\bin
     ```
   - Start Kibana:
     ```powershell
     .\kibana.bat
     ```
   - Wait for Kibana to start (look for a message like “Status changed from yellow to green - Ready” in the console).

4. **Verify Kibana**:
   - Open a browser and navigate to `http://localhost:5601`.
   - Log in with the `elastic` user and the password from Elasticsearch.
   - You should see the Kibana dashboard. Since no data is indexed yet, you won’t see logs until Winlogbeat is configured.

#### **Step 3: Install Logstash**
1. **Download and Extract**:
   - Download the Logstash ZIP file from [Elastic downloads](https://www.elastic.co/downloads/logstash) (e.g., `logstash-8.17.2-windows-x86_64.zip`).
   - Extract it to `E:\Hacking\ELK Stack` and rename the folder to `logstash` (e.g., `E:\Hacking\ELK Stack\logstash`).

2. **Create a Logstash Configuration File**:
   - Create a file named `logstash.conf` in `E:\Hacking\ELK Stack\logstash\config`.
   - Add a basic configuration to process logs from Winlogbeat and send them to Elasticsearch:
     ```yaml
     input {
       beats {
         port => 5044
       }
     }
     output {
       elasticsearch {
         hosts => ["http://localhost:9200"]
         index => "winlogbeat-%{+YYYY.MM.dd}"
         user => "elastic"
         password => "your_elastic_password"
       }
       stdout { codec => rubydebug }
     }
     ```
     Replace `your_elastic_password` with the Elasticsearch password, if you have any. No password needed for my device, just paste the above.

     
   - Run Logstash in CMD(Amdin):
     ```powershell
     .\logstash.bat -f "C:\ELK\logstash-9.1.3\config\logstash.conf"
     ```

#### **Step 4: Install and Configure Winlogbeat**
1. **Download and Extract**:
   - Download Winlogbeat from [Elastic downloads](https://www.elastic.co/downloads/beats/winlogbeat) (e.g., `winlogbeat-8.17.2-windows-x86_64.zip`).
   - Extract it to `E:\Hacking\ELK Stack` and rename the folder to `winlogbeat` (e.g., `E:\Hacking\ELK Stack\winlogbeat`).

2. **Configure Winlogbeat**:
   - Open `E:\Hacking\ELK Stack\winlogbeat\winlogbeat.yml` in a text editor.
   - Configure it to collect Windows security event logs and send them to Logstash:
     ```yaml
      winlogbeat.event_logs:
        - name: Security
          ignore_older: 72h
        - name: System
        - name: Application
        - name: Microsoft-Windows-Sysmon/Operational
      
      output.logstash:
        hosts: ["127.0.0.1:5044"]
     ```
   - Save the file.

3. **Install Winlogbeat as a Service**:
   - Open PowerShell as Administrator and navigate to the Winlogbeat directory:
     ```powershell
     cd E:\Hacking\ELK Stack\winlogbeat
     ```
   - Install the service:
     ```powershell
     PowerShell.exe -ExecutionPolicy UnRestricted -File .\install-service-winlogbeat.ps1
     ```
   - Start the service:
     ```powershell
     Start-Service winlogbeat
     ```

     If you find that less data is coming, you stop the service using this:
     ```powershell
     Stop-Service winlogbeat
     ```

     Then run this:
     ```powershell
     .\winlogbeat.exe -e -c winlogbeat.yml
     ```

#### **Step 5: Enhance Security Monitoring with Sysmon (Optional but Recommended)**
1. **Install Sysmon**:
   - Download Sysmon from [Microsoft Sysinternals](https://docs.microsoft.com/en-us/sysinternals/downloads/sysmon).
   - Install Sysmon with a configuration file (e.g., SwiftOnSecurity’s config) for detailed security event logging:
     ```powershell
     sysmon64.exe -i sysmonconfig-export.xml
     ```
     Find a recommended configuration file from [SwiftOnSecurity’s GitHub](https://github.com/SwiftOnSecurity/sysmon-config).

     I used the following:
     ```xml
     <Sysmon schemaversion="4.81">
        <EventFiltering>
          <RuleGroup name="" groupRelation="or">
            <ProcessCreate onmatch="exclude">
              <Image condition="is">C:\Windows\System32\svchost.exe</Image>
              <Image condition="is">C:\Windows\System32\csrss.exe</Image>
              <Image condition="is">C:\Windows\System32\smss.exe</Image>
              <Image condition="is">C:\Windows\System32\winlogon.exe</Image>
              <Image condition="is">C:\Windows\System32\services.exe</Image>
              <Image condition="is">C:\Windows\System32\lsass.exe</Image>
              <Image condition="is">C:\Windows\System32\wininit.exe</Image>
              <Image condition="is">C:\Windows\System32\dwm.exe</Image>
              <Image condition="is">C:\Windows\System32\taskhostw.exe</Image>
            </ProcessCreate>
          </RuleGroup>
          <RuleGroup name="" groupRelation="or">
            <NetworkConnect onmatch="include">
              <DestinationPort name="Common Ports" condition="is">80</DestinationPort>
              <DestinationPort name="Common Ports" condition="is">443</DestinationPort>
              <DestinationPort name="Common Ports" condition="is">3389</DestinationPort>
              <DestinationPort name="Common Ports" condition="is">445</DestinationPort>
            </NetworkConnect>
          </RuleGroup>
          <RuleGroup name="" groupRelation="or">
            <FileCreate onmatch="include">
              <TargetFilename condition="contains">\AppData\Local\Temp\</TargetFilename>
              <TargetFilename condition="contains">\Downloads\</TargetFilename>
              <TargetFilename condition="end with">.exe</TargetFilename>
              <TargetFilename condition="end with">.dll</TargetFilename>
            </FileCreate>
          </RuleGroup>
          <RuleGroup name="" groupRelation="or">
            <RegistryEvent onmatch="include">
              <TargetObject condition="contains">HKLM\Software\Microsoft\Windows\CurrentVersion\Run</TargetObject>
              <TargetObject condition="contains">HKCU\Software\Microsoft\Windows\CurrentVersion\Run</TargetObject>
            </RegistryEvent>
          </RuleGroup>
          <RuleGroup name="" groupRelation="or">
            <FileDelete onmatch="include">
              <TargetFilename name="T1070.004" condition="contains">\Users\</TargetFilename>
              <TargetFilename name="T1070.004" condition="contains">\AppData\Local\Temp\</TargetFilename>
              <TargetFilename name="T1070.004" condition="contains">\Downloads\</TargetFilename>
              <Image name="T1070.004" condition="contains">\AppData\Local\Temp\</Image>
              <Image name="T1070.004" condition="contains">Revenge-RAT</Image>
              <TargetFilename name="T1070.004" condition="end with">.exe</TargetFilename>
              <TargetFilename name="T1070.004" condition="end with">.dll</TargetFilename>
              <TargetFilename name="T1070.004" condition="end with">.sys</TargetFilename>
            </FileDelete>
          </RuleGroup>
          <RuleGroup name="" groupRelation="or">
            <FileDelete onmatch="exclude">
              <Image condition="is">C:\Windows\System32\svchost.exe</Image>
              <Image condition="contains">explorer.exe</Image>
              <TargetFilename condition="contains">\Temp\~</TargetFilename>
            </FileDelete>
          </RuleGroup>
        </EventFiltering>
      </Sysmon>
     ```

     To update `sysmonconfig.xml` use this command:
     ```powershell
     Sysmon64.exe -c sysmonconfig-export.xml
     ```

     To see the current `xml` use this:
     ```powershell
     Sysmon64.exe -c
     ```

#### **Step 6: Analyze Logs in Kibana**
1. **Access Kibana**:
   - Navigate to `http://localhost:5601` and log in with the `elastic` user and password.

2. **Create an Index Pattern**:
   - In Kibana, go to “Stack Management” > “Kibana” > “Data Views” > Create (name, index both will be `winlogbeat-*`)
   - Import the Winlogbeat dashboard from the [Elastic downloads page](https://www.elastic.co/downloads/beats/winlogbeat) or search for it in “Kibana Apps.”
   - Use the dashboard to monitor security events like logon failures (Event ID 4625), new service installations (Event ID 4798), or suspicious PowerShell activity (Sysmon Event ID 3).
---










