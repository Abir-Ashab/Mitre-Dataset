1) Run the following by going to `E:\Hacking\ELK Stack\elasticsearch-9.1.1\bin`
    ```powershell
    elasticsearch.bat
    ```
2) Run the following by going to by going to `E:\Hacking\ELK Stack\kibana-9.1.1\bin` (as admin) 
    ```powershell
    kibana.bat
    ```
3) Run the following by going to by going to `E:\Hacking\ELK Stack\logstash-9.1.1\bin` 
    ```powershell
    .\logstash.bat -f "E:\Hacking\ELK Stack\logstash-9.1.1\config\logstash.conf"
    ```

4) If it is not working, try this check:
    ```powershell
    Get-Service winlogbeat
    Get-Service sysmon64
    ```

    If any of the above not running, do this:
    ```powershell
    Start-Service winlogbeat
    Start-Service sysmon64
    ```
5) Run `aw-qt.exe` from `E:\Hacking\ELK Stack\activitywatch` (just double click, nothing will show, go check the link, it will work)

6) Here is the link of all 3 logs:
    ```powershell
    http://localhost:5601/		    kibana
    http://localhost:9200/		    elastic
    http://localhost:5600/#/home	activitywatch
    ```