* **Direction:** `10.43.0.105 → 150.171.27.10:443` (internal host → external IP)
* **Length:** 54 bytes (small)
* **TCP flags:** `A` (ACK, no data)
* **No payload layer** (like Raw or Padding)

### ⚠ Why it is indicating C2 traffic:

1. **Small, repeated packets** like this are typical of RAT beaconing.
2. The external IP (`150.171.27.10`) is not a standard website or service.
3. The TCP connection uses **ACK-only** packets, suggesting keep-alive signals rather than web browsing.
4. The **sequence of packet numbers** over time may show periodic intervals — classic for RATs like RevengeRAT.
