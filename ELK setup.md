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
     cd "E:\Hacking\ELK Stack\elasticsearch-9.0.2"
     ```
   - Run the service installation script:
     ```powershell
     .\elasticsearch-service.bat install
     ```
   - Start the service:
     ```powershell
     .\elasticsearch-service.bat start
     ```
   - During the first startup, Elasticsearch generates a default password for the `elastic` user. Check the output in the PowerShell window or the logs in `E:\Hacking\ELK Stack\elasticsearch\logs` for the password. Save it for later use.
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
     elasticsearch.username: "elastic"
     elasticsearch.password: "your_elastic_password"
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
     ```conf
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

3. **Install Logstash as a Service**:
   - Download NSSM (Non-Sucking Service Manager) from [nssm.cc](https://nssm.cc/download) and extract it to `E:\Hacking\ELK Stack\nssm`.
   - In PowerShell, navigate to the NSSM directory:
     ```powershell
     cd E:\Hacking\ELK Stack\nssm\win64
     ```
   - Install Logstash as a service:
     ```powershell
     .\nssm.exe install logstash
     ```
   - In the NSSM GUI:
     - Set the “Path” to `E:\Hacking\ELK Stack\logstash\bin\logstash.bat`.
     - Set the “Startup directory” to `E:\Hacking\ELK Stack\logstash\bin`.
     - In the “Arguments” field, enter:
       ```
       -f E:\Hacking\ELK Stack\logstash\config\logstash.conf
       ```
     - Click “Install service.”
   - Start the service:
     ```powershell
     .\nssm.exe start logstash
     ```

4. **Verify Logstash**:
   - Check the logs in `E:\Hacking\ELK Stack\logstash\logs` to ensure Logstash starts without errors and is listening on port 5044.

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

4. **Verify Winlogbeat**:
   - Check the logs in `E:\Hacking\ELK Stack\winlogbeat\logs` to ensure Winlogbeat is sending data to Logstash without errors.

#### **Step 5: Enhance Security Monitoring with Sysmon (Optional but Recommended)**
1. **Install Sysmon**:
   - Download Sysmon from [Microsoft Sysinternals](https://docs.microsoft.com/en-us/sysinternals/downloads/sysmon).
   - Install Sysmon with a configuration file (e.g., SwiftOnSecurity’s config) for detailed security event logging:
     ```powershell
     sysmon64.exe -i sysmonconfig-export.xml
     ```
     Find a recommended configuration file from [SwiftOnSecurity’s GitHub](https://github.com/SwiftOnSecurity/sysmon-config).

2. **Update Winlogbeat Configuration**:
   - Add the Sysmon event log channel to `winlogbeat.yml`:
     ```yaml
     winlogbeat.event_logs:
       - name: Security
         ignore_older: 72h
       - name: System
       - name: Application
       - name: Microsoft-Windows-Sysmon/Operational
     ```
   - Restart the Winlogbeat service:
     ```powershell
     Restart-Service winlogbeat
     ```

#### **Step 6: Analyze Logs in Kibana**
1. **Access Kibana**:
   - Navigate to `http://localhost:5601` and log in with the `elastic` user and password.

2. **Create an Index Pattern**:
   - In Kibana, go to “Stack Management” > “Index Patterns.”
   - Create a new index pattern for `winlogbeat-*`.
   - Select `@timestamp` as the time field and create the pattern.

3. **Set Up Dashboards for Security Threats**:
   - Go to “Analytics” > “Discover” to view raw logs.
   - Install the Winlogbeat dashboard for pre-built visualizations:
     - In Kibana, go to “Stack Management” > “Kibana” > “Data Views” or “Dashboards.”
     - Import the Winlogbeat dashboard from the [Elastic downloads page](https://www.elastic.co/downloads/beats/winlogbeat) or search for it in “Kibana Apps.”
   - Use the dashboard to monitor security events like logon failures (Event ID 4625), new service installations (Event ID 4798), or suspicious PowerShell activity (Sysmon Event ID 3).

4. **Configure Alerts for Security Threats**:
   - In Kibana, go to “Security” or “Alerting” to create rules for detecting anomalies, such as:
     - Multiple failed logon attempts (Event ID 4625).
     - Suspicious network connections logged by Sysmon.
   - Example rule: Create a query for `event.code: 4625` with a threshold of 5 occurrences in 10 minutes to trigger an alert.

#### **Step 7: Secure the ELK Stack**
1. **Enable SSL/TLS**:
   - Generate certificates for Elasticsearch and Kibana using the `elasticsearch-certutil` tool:
     ```powershell
     cd E:\Hacking\ELK Stack\elasticsearch\bin
     .\elasticsearch-certutil http
     ```
     Follow the prompts to generate certificates and place them in `E:\Hacking\ELK Stack\elasticsearch\config\certs`.
   - Update `elasticsearch.yml` and `kibana.yml` to use these certificates, as described in [Elastic’s security documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/security-basic-setup.html).

2. **Configure Access Controls**:
   - Create additional users in Kibana under “Stack Management” > “Users” to restrict access.
   - Use NGINX as a reverse proxy for Kibana to add an extra layer of security, as described in [Logit.io’s guide](https://logit.io/blog/post/complete-guide-to-elk-2024).[](https://logit.io/blog/post/elk-stack-guide/)

3. **Enable Audit Logging**:
   - In `elasticsearch.yml`, enable audit logging:
     ```yaml
     xpack.security.audit.enabled: true
     ```
   - This logs all user and system activity for compliance and monitoring.

#### **Step 8: Test and Monitor**
1. **Generate Test Events**:
   - Trigger security events (e.g., failed logins or PowerShell commands) to ensure logs are captured.
   - Example: Run a PowerShell command to simulate malicious activity:
     ```powershell
     powershell -exec bypass -nop -w hidden "IEX ((new-object net.webclient).downloadstring('https://www.google.com'))"
     ```
   - Check Kibana’s Discover tab for corresponding Sysmon logs (Event ID 3).

2. **Monitor Dashboards**:
   - Use the Winlogbeat dashboard to track event IDs, sources, and levels.
   - Look for patterns like repeated logon failures or unusual process executions.

3. **Optimize for Production**:
   - Increase Elasticsearch heap size in `E:\Hacking\ELK Stack\elasticsearch\config\jvm.options` (e.g., `-Xms2g -Xmx2g` for 4 GB RAM).
   - Set up log rotation to manage disk space.
   - Consider a multi-node setup for high availability in production environments.

---
