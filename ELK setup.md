## Prerequisites:

* Windows 10/11 or Server.
* Java (for Logstash, if used).
* Enough RAM (ELK components are resource-heavy).

##  Step-by-Step Guide (Windows)

---

### Step 1: Download & Install ELK Stack

#### 1.1 Install **Elasticsearch**

* Download: [https://www.elastic.co/downloads/elasticsearch](https://www.elastic.co/downloads/elasticsearch)
* Extract the zip.
* Replace the **config/elasticsearch.yml** with the following:
```yml
xpack.security.enabled: false
xpack.security.enrollment.enabled: true
xpack.security.http.ssl:
enabled: false
keystore.path: certs/http.p12
xpack.security.transport.ssl:
enabled: true
verification_mode: certificate
keystore.path: certs/transport.p12
truststore.path: certs/transport.p12
cluster.initial_master_nodes: ["DESKTOP-NCN90P2"]
http.host: 0.0.0.0
```

* Open a terminal (PowerShell or CMD), navigate to the bin folder:

```sh
cd C:\elasticsearch\bin
elasticsearch.bat
```

or click on the file, and click **run as administrator**

* Access: [http://localhost:9200](http://localhost:9200)

#### 1.2 Install **Kibana**

* Download: [https://www.elastic.co/downloads/kibana](https://www.elastic.co/downloads/kibana)
* Extract it.
* Replace the **config/elasticsearch.yml** with the following:
```yml
server.host: "0.0.0.0"
server.port: 5601
elasticsearch.hosts: ["http://localhost:9200"]
    ```
* Run:

```sh
cd C:\kibana\bin
kibana.bat
```

or click on the file, and click **run as administrator**

* Access: [http://localhost:5601](http://localhost:5601)

#### (Optional) 1.3 Install **Logstash** (if you need parsing/filtering)

* Download: [https://www.elastic.co/downloads/logstash](https://www.elastic.co/downloads/logstash)
* Extract it. Logstash is optional if you use Filebeat → Elasticsearch directly.

---

### Step 2: Install & Configure Filebeat

#### 2.1 Download Filebeat

* Download: [https://www.elastic.co/downloads/beats/filebeat](https://www.elastic.co/downloads/beats/filebeat)
* Extract it, e.g., `C:\filebeat`.

#### 2.2 Enable Windows Event Log Module

Open PowerShell in the Filebeat folder:

```powershell
cd C:\filebeat
.\filebeat.exe modules enable windows
```

#### 2.3 Configure Filebeat

Edit `filebeat.yml` in Notepad or VS Code:

```yaml
# Output to Elasticsearch
output.elasticsearch:
  hosts: ["localhost:9200"]

# Optional: to visualize dashboards in Kibana
setup.kibana:
  host: "localhost:5601"
```

(If you want to use Logstash instead of Elasticsearch, just switch the `output.elasticsearch` block with `output.logstash`.)

---

### Step 3: Run Filebeat

#### 3.1 Setup dashboards and ingest pipelines:

```powershell
.\filebeat.exe setup
```

#### 3.2 Start Filebeat

To run it manually for testing:

```powershell
.\filebeat.exe -e
```

Or install as a Windows service:

```powershell
.\install-service-filebeat.ps1
Start-Service filebeat
```

---

### Step 4: View Logs in Kibana

1. Open Kibana: [http://localhost:5601](http://localhost:5601)
2. Go to **“Discover”**
3. Create index pattern: `filebeat-*`
4. View logs like:

   * Security logs
   * System events
   * Application logs

---

## Optional: Monitor Specific Log Files

You can modify `filebeat.inputs` section in `filebeat.yml` to watch custom log files:

```yaml
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - C:\Logs\myapp.log
```

---
