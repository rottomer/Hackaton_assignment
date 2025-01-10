import socket
import struct
import threading
import time
import signal
import sys

# Configuration
BROADCAST_PORT = 13117
MAGIC_COOKIE = 0xabcddcba
MESSAGE_TYPE = 0x2
UDP_SERVER_PORT = 2025
TCP_SERVER_PORT = 2026

running = True  # Global flag to control the server's loop

def broadcast_offers():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as broadcast_socket:
        broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        broadcast_socket.bind(('', 0))  # Use any available port for sending

        message = struct.pack(
            '!IBHH',
            MAGIC_COOKIE,
            MESSAGE_TYPE,
            UDP_SERVER_PORT,
            TCP_SERVER_PORT
        )
        
        while running:
            broadcast_socket.sendto(message, ('<broadcast>', BROADCAST_PORT))
            print("Offer broadcast sent.")
            time.sleep(1)  # Broadcast every second

def handle_tcp_client(client_socket, client_address):
    try:
        print(f"TCP connection established with {client_address}")
        # Read file size request from the client
        request = client_socket.recv(1024).decode().strip()
        if request.isdigit():
            file_size = int(request)
            print(f"Client requested {file_size} bytes")

            # Send the requested amount of data
            data = b'0' * file_size  # Example data (all zeros)
            client_socket.sendall(data)
            print(f"Sent {file_size} bytes to {client_address}")
        else:
            print("Invalid request received.")
    except Exception as e:
        print(f"Error handling TCP client {client_address}: {e}")
    finally:
        client_socket.close()

def start_tcp_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_server:
        tcp_server.bind(('', TCP_SERVER_PORT))
        tcp_server.listen(5)
        tcp_server.settimeout(1)  # Set a timeout of 1 second for the accept() call
        print(f"TCP server listening on port {TCP_SERVER_PORT}")

        while running:
            try:
                client_socket, client_address = tcp_server.accept()
                threading.Thread(target=handle_tcp_client, args=(client_socket, client_address), daemon=True).start()
            except socket.timeout:
                continue  # Retry the loop on timeout

def signal_handler(sig, frame):
    global running
    print("\nShutting down the server...")
    running = False

if __name__ == "__main__":
    # Register signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    print("Server starting...")

    # Start broadcasting thread
    broadcast_thread = threading.Thread(target=broadcast_offers, daemon=True)
    broadcast_thread.start()

    # Start TCP server
    try:
        start_tcp_server()
    except KeyboardInterrupt:
        print("\nServer stopped.")
