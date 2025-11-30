## 1️⃣ Key indicators for a download in your logs

1. **Server → Client direction**

   * Check `IP.src` and `IP.dst`:

     ```json
     "IP": { "src": "server_ip", "dst": "client_ip" }
     ```

     * If `src` is the remote server (like `31.216.145.5`) and `dst` is your local IP, it might be a download.

2. **Non-zero TCP payload**

   * Look at `TCP` flags and payload (`Raw.load` or `tcp.len`):

     * **Non-zero TCP payload**: indicates actual data transfer.
     * `Raw.load` contains bytes of the download.
   * For example:

     ```json
     "TCP": { "flags": "PA" } 
     "Raw": { "load": "b'...'" }
     ```

     * `PA` → PSH+ACK, usually carries data.

3. **Packet size**

   * If `length` (IP or frame length) > 500–1000 bytes, it’s likely a data packet. Use regex:
   ```js
   "length":\s*[5-9]\d\d
   ```
   * Control packets (ACK, SYN-ACK) are usually < 100 bytes.

4. **Sequence of packets**

   * Downloads usually appear as a **series of consecutive packets from server → client**.
   * Many consecutive `Raw.load` packets from the same source to the client usually indicate a download stream.

5. **Look for “https / Raw” in `summary`**

   * Example:

     ```json
     "summary": "Ether / IP / TCP 31.216.145.5:https > 10.43.0.105:61766 PA / Raw"
     ```
   * `PA / Raw` → data sent (PUSH+ACK with payload).

---