import socket
import struct
import threading
import time

# Configuration
BROADCAST_PORT = 13117  # The port to broadcast on
MAGIC_COOKIE = 0xabcddcba
MESSAGE_TYPE = 0x2
UDP_SERVER_PORT = 2025  # Placeholder port for UDP
TCP_SERVER_PORT = 2026  # Placeholder port for TCP

def broadcast_offers():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as broadcast_socket:
        broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        broadcast_socket.bind(('', 0))  # Use any available port for sending

        message = struct.pack(
            '!IBHH',  # Format: 4 bytes for magic cookie, 1 byte for type, 2 bytes for UDP, 2 bytes for TCP
            MAGIC_COOKIE,
            MESSAGE_TYPE,
            UDP_SERVER_PORT,
            TCP_SERVER_PORT
        )
        
        while True:
            broadcast_socket.sendto(message, ('<broadcast>', BROADCAST_PORT))
            print("Offer broadcast sent.")
            time.sleep(1)  # Broadcast every second

if __name__ == "__main__":
    print("Server starting...")
    broadcast_thread = threading.Thread(target=broadcast_offers, daemon=True)
    broadcast_thread.start()

    print("Server is broadcasting offers. Press Ctrl+C to exit.")
    while True:
        time.sleep(1)  # Keep the main thread alive
