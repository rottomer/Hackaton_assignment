import socket
import struct

# Configuration
BROADCAST_PORT = 13117  # The same port used by the server
MAGIC_COOKIE = 0xabcddcba
MESSAGE_TYPE = 0x2

def listen_for_offers():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as listen_socket:
        listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listen_socket.bind(('', BROADCAST_PORT))  # Listen on the broadcast port

        print(f"Listening for offers on port {BROADCAST_PORT}...")
        while True:
            message, addr = listen_socket.recvfrom(1024)  # Buffer size of 1024 bytes
            print(f"Received message from {addr}: {message}")

            # Validate message format
            try:
                magic_cookie, message_type, udp_port, tcp_port = struct.unpack('!IBHH', message)
                if magic_cookie == MAGIC_COOKIE and message_type == MESSAGE_TYPE:
                    print(f"Valid offer received: UDP Port={udp_port}, TCP Port={tcp_port}")
                else:
                    print("Invalid offer received!")
            except struct.error:
                print("Failed to parse message.")

if __name__ == "__main__":
    listen_for_offers()
