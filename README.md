# Network Speed Test Application

This project is a **client-server application** for performing network speed tests over **TCP** and **UDP**.
The client and server are designed to work together to measure download speeds, transfer times, and packet loss under various configurations.

---

## Features

- **Client**:
  - Connects to the server via TCP and UDP.
  - Measures:
    - Transfer time.
    - Transfer speed (Mbps).
    - Percentage of successful packets (UDP).
  - Supports multiple parallel TCP and UDP connections.

- **Server**:
  - Broadcasts availability via UDP.
  - Handles multiple client requests simultaneously.
  - Simulates data transfers using random payloads.

---

## Requirements

- **Python Version**: 3.6+
- **Dependencies**:
  - `colorama`: For colored terminal output.

  Install dependencies:
  ```bash
  pip install colorama
