# Network Speed Test Application

A client-server application that performs network speed tests over **TCP** and **UDP**, designed to measure download speed, transfer time, and packet loss in a controlled environment. The system simulates real-world scenarios, offering insights into network performance and behavior.

---

## Features
- **Server**:
  - Broadcasts availability via UDP offers.
  - Responds to client requests for file transfers using TCP and UDP.
  - Handles multiple clients concurrently.

- **Client**:
  - Discovers available servers using UDP.
  - Measures:
    - Transfer time.
    - Download speed (in Mbps).
    - Packet loss percentage for UDP transfers.
  - Supports multiple simultaneous TCP and UDP connections.

---

## Requirements
- **Python Version**: Python 3.6 or newer.
- **Dependencies**:
  - `colorama` (for colored terminal output).

  Install dependencies using:
  ```bash
  pip install colorama
  ```

---

## File Structure
```plaintext
├── server.py        # Server application
├── client.py        # Client application
├── tests/           # Test scripts for debugging and validation
├── README.md        # Project documentation
```

---

## Setup Instructions
1. **Clone the Repository**:
   ```bash
   git clone <https://github.com/rottomer/Hackaton_assignment>
   cd <Hackaton_assignment>
   ```

2. **Start the Server**:
   ```bash
   python server.py
   ```

3. **Start the Client**:
   ```bash
   python client.py
   ```

---

## Usage
### 1. Running the Server
- Start the server. It will:
  - Broadcast its availability via UDP every second.
  - Listen for incoming TCP and UDP connections on designated ports.

### 2. Running the Client
- Start the client and follow the prompts:
  - Enter the file size (in bytes).
  - Enter the number of TCP connections.
  - Enter the number of UDP connections.
- The client will:
  - Discover available servers via UDP.
  - Establish TCP and UDP connections with the server.
  - Perform file transfers and log the results.

---

## Output Examples

### Server Output
```plaintext
[12:00:00] Server starting...
[12:00:01] Offer broadcast sent.
[12:00:02] TCP connection established with ('192.168.1.5', 54321)
[12:00:03] UDP transfer to ('192.168.1.5', 54321) completed.
```

### Client Output
```plaintext
[12:00:00] Client started, listening for offer requests on port 13117...
[12:00:01] Received offer from 192.168.1.5, UDP port: 2025, TCP port: 2026
[12:00:02] Connected to server at 192.168.1.5:2026 via TCP
[12:00:03] UDP transfer finished, total time: 2.00 seconds
[12:00:03] Metric                  Value
Total Time (seconds)          2.00
Speed (Mbps)                  5.12
Packet Success (%)           100.00
```

---

## Performance Metrics
The application measures the following metrics for each transfer:
- **TCP**:
  - Transfer time.
  - Speed (in Mbps).
- **UDP**:
  - Transfer time.
  - Speed (in Mbps).
  - Percentage of successful packets (packet loss).

---

## Testing
Test scripts are provided in the `tests/` folder to validate:
1. UDP broadcast reception.
2. TCP data transfer.
3. UDP packet handling and loss calculation.

---

## Contributors
- Tomer Rothman, ID: 315839795 ([GitHub Profile](https://github.com/rottomer))
- May-Tal Wexler, ID: 209638667 ([GitHub Profile](https://github.com/May-talWex))
