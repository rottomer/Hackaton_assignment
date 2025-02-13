# server.py
import socket
import struct
import threading
import time
from datetime import datetime
from colorama import Fore, Style, init

# Initialize colorama for styled output
init(autoreset=True)

# Configuration
BROADCAST_PORT = 13117
MAGIC_COOKIE = 0xabcddcba
MESSAGE_TYPE = 0x2
UDP_SERVER_PORT = 2025
TCP_SERVER_PORT = 2026

running = True

# Logging function with timestamps
def log(message, color=Fore.RESET):
    print(color + f"[{datetime.now().strftime('%H:%M:%S')}] {message}" + Style.RESET_ALL)

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
            broadcast_socket.sendto(message, ('255.255.255.255', BROADCAST_PORT))
            log("Offer broadcast sent.", Fore.CYAN)
            time.sleep(1)

def handle_udp_client(client_address, file_size):
    try:
        log(f"Starting UDP transfer to {client_address}", Fore.YELLOW)

        # Prepare the data to send
        total_segments = (file_size + 1023) // 1024
        sequence_number = 0

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            while sequence_number < total_segments:
                payload = b'0' * 1024
                message = struct.pack(
                    '!IBQQ',
                    MAGIC_COOKIE,
                    0x4,
                    total_segments,
                    sequence_number
                ) + payload

                udp_socket.sendto(message, client_address)
                sequence_number += 1
                time.sleep(0.001)  # Prevent congestion

        log(f"UDP transfer to {client_address} completed.", Fore.GREEN)
    except Exception as e:
        log(f"Error handling UDP client {client_address}: {e}", Fore.RED)

def start_udp_server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_server:
        udp_server.settimeout(1)  # Prevent infinite blocking
        udp_server.settimeout(1)
        log(f"UDP server listening on port {UDP_SERVER_PORT}", Fore.CYAN)

        while running:
            try:
                message, client_address = udp_server.recvfrom(1024)
                magic_cookie, message_type, file_size = struct.unpack('!IBQ', message)
                if magic_cookie != MAGIC_COOKIE or message_type != 0x3:
                    log("Invalid UDP request received.", Fore.RED)
                    continue

                log(f"Received UDP request from {client_address} for {file_size} bytes.", Fore.GREEN)
                threading.Thread(target=handle_udp_client, args=(client_address, file_size), daemon=True).start()
            except socket.timeout:
                continue
            except Exception as e:
                log(f"Error in UDP server: {e}", Fore.RED)

def handle_tcp_client(client_socket, client_address):
    try:
        log(f"TCP connection established with {client_address}", Fore.YELLOW)
        request = client_socket.recv(1024).decode().strip()
        if request.isdigit():
            file_size = int(request)
            log(f"Client requested {file_size} bytes", Fore.GREEN)

            data = b'0' * file_size
            client_socket.sendall(data)
            log(f"Sent {file_size} bytes to {client_address}", Fore.GREEN)
        else:
            log("Invalid TCP request received.", Fore.RED)
    except Exception as e:
        log(f"Error handling TCP client {client_address}: {e}", Fore.RED)
    finally:
        client_socket.close()

def start_tcp_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_server:
        tcp_server.bind(('', TCP_SERVER_PORT))
        tcp_server.listen(5)
        log(f"TCP server listening on port {TCP_SERVER_PORT}", Fore.CYAN)

        while running:
            try:
                client_socket, client_address = tcp_server.accept()
                threading.Thread(target=handle_tcp_client, args=(client_socket, client_address), daemon=True).start()
            except socket.timeout:
                continue
            except Exception as e:
                log(f"Error in TCP server: {e}", Fore.RED)

def signal_handler(sig, frame):
    global running
    log("Shutting down the server...", Fore.RED)
    running = False

if __name__ == "__main__":
    import signal
    signal.signal(signal.SIGINT, signal_handler)

    log("Server starting...", Fore.GREEN)

    broadcast_thread = threading.Thread(target=broadcast_offers, daemon=True)
    broadcast_thread.start()

    tcp_thread = threading.Thread(target=start_tcp_server, daemon=True)
    tcp_thread.start()

    udp_thread = threading.Thread(target=start_udp_server, daemon=True)
    udp_thread.start()

    while running:
        time.sleep(1)

    log("Server shut down.", Fore.RED)