## View Saved Wi-Fi Passwords (Command Prompt/CMD)

* To see all the Wi-Fi network names:   
  *netsh wlan show profiles*  
* Then for a specific profile:  
  *netsh wlan show profile name="YourNetworkName" key=clear*  
* Look under:   
  *Key Content: your\_wifi\_password*

