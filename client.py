# client.py
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
OFFER_MESSAGE_TYPE = 0x2
REQUEST_MESSAGE_TYPE = 0x3
PAYLOAD_MESSAGE_TYPE = 0x4

# Logging function with timestamps
def log(message, color=Fore.RESET):
    print(color + f"[{datetime.now().strftime('%H:%M:%S')}] {message}" + Style.RESET_ALL)

def listen_for_offers():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as client_socket:
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        client_socket.bind(('', BROADCAST_PORT))
        log(f"Client started, listening for offer requests on port {BROADCAST_PORT}...", Fore.CYAN)

        while True:
            try:
                message, server_address = client_socket.recvfrom(1024)
                magic_cookie, message_type, udp_port, tcp_port = struct.unpack('!IBHH', message)
                if magic_cookie != MAGIC_COOKIE or message_type != OFFER_MESSAGE_TYPE:
                    log("Received invalid offer message.", Fore.RED)
                    continue
                log(f"Received offer from {server_address[0]}, UDP port: {udp_port}, TCP port: {tcp_port}", Fore.GREEN)
                return server_address[0], udp_port, tcp_port
            except Exception as e:
                log(f"Error receiving offer: {e}", Fore.RED)

def send_udp_request(server_ip, udp_port, file_size):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_client:
        udp_client.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1048576)  # Increase buffer size to 1MB

        request_message = struct.pack('!IBQ', MAGIC_COOKIE, REQUEST_MESSAGE_TYPE, file_size)
        udp_client.sendto(request_message, (server_ip, udp_port))
        log(f"Sent UDP request to {server_ip}:{udp_port} for {file_size} bytes.", Fore.YELLOW)

        received_packets = set()
        total_segments = None
        start_time = time.time()

        udp_client.settimeout(2)
        while True:
            try:
                data, addr = udp_client.recvfrom(2048)
                magic_cookie, message_type, total_segments_received, sequence_number = struct.unpack('!IBQQ', data[:21])
                if magic_cookie != MAGIC_COOKIE or message_type != PAYLOAD_MESSAGE_TYPE:
                    log("Received invalid payload message.", Fore.RED)
                    continue
                if total_segments is None:
                    total_segments = total_segments_received
                received_packets.add(sequence_number)
            except socket.timeout:
                log("No more data received. UDP transfer complete.", Fore.YELLOW)
                break
            except Exception as e:
                log(f"Error receiving UDP data: {e}", Fore.RED)
                break

        end_time = time.time()
        total_time = end_time - start_time
        packets_received = len(received_packets)
        packet_loss = ((total_segments - packets_received) / total_segments) * 100 if total_segments else 0
        speed = (packets_received * 1024 * 8) / total_time  # Bits per second

        log(f"UDP transfer finished, total time: {total_time:.2f} seconds", Fore.GREEN)
        log(f"Total speed: {speed / (1024 * 1024):.2f} Mbps", Fore.CYAN)
        if packet_loss > 0:
            log(f"Percentage of packets received successfully: {100 - packet_loss:.2f}%", Fore.RED)
        else:
            log(f"Percentage of packets received successfully: {100 - packet_loss:.2f}%", Fore.GREEN)

def send_tcp_request(server_ip, tcp_port, file_size):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_client:
            tcp_client.connect((server_ip, tcp_port))
            log(f"Connected to server at {server_ip}:{tcp_port} via TCP", Fore.YELLOW)

            tcp_client.sendall(f"{file_size}\n".encode())
            log(f"Requested {file_size} bytes over TCP", Fore.GREEN)

            start_time = time.time()
            received_data = b""
            while len(received_data) < file_size:
                chunk = tcp_client.recv(4096)
                if not chunk:
                    break
                received_data += chunk
            end_time = time.time()

            total_time = end_time - start_time
            speed = (len(received_data) * 8) / total_time  # Bits per second
            log(f"TCP transfer finished, total time: {total_time:.2f} seconds", Fore.GREEN)
            log(f"Total speed: {speed / (1024 * 1024):.2f} Mbps", Fore.CYAN)
    except Exception as e:
        log(f"Error in TCP transfer: {e}", Fore.RED)

if __name__ == "__main__":
    file_size = int(input(Fore.CYAN + "Enter the file size in bytes: " + Style.RESET_ALL))
    num_tcp_connections = int(input(Fore.CYAN + "Enter the number of TCP connections: " + Style.RESET_ALL))
    num_udp_connections = int(input(Fore.CYAN + "Enter the number of UDP connections: " + Style.RESET_ALL))

    while True:
        server_ip, udp_port, tcp_port = listen_for_offers()

        log("Starting transfers...", Fore.CYAN)
        threads = []

        for i in range(num_tcp_connections):
            t = threading.Thread(target=send_tcp_request, args=(server_ip, tcp_port, file_size))
            threads.append(t)
            t.start()

        for i in range(num_udp_connections):
            t = threading.Thread(target=send_udp_request, args=(server_ip, udp_port, file_size))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        log("All transfers complete, listening for new offers...", Fore.GREEN)