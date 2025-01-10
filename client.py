import socket
import struct
import threading
import time

# Configuration
BROADCAST_PORT = 13117
MAGIC_COOKIE = 0xabcddcba
OFFER_MESSAGE_TYPE = 0x2
REQUEST_MESSAGE_TYPE = 0x3
PAYLOAD_MESSAGE_TYPE = 0x4

def listen_for_offers():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as client_socket:
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        client_socket.bind(('', BROADCAST_PORT))
        print(f"Client started, listening for offer requests on port {BROADCAST_PORT}...")

        while True:
            try:
                message, server_address = client_socket.recvfrom(1024)
                magic_cookie, message_type, udp_port, tcp_port = struct.unpack('!IBHH', message)
                if magic_cookie != MAGIC_COOKIE or message_type != OFFER_MESSAGE_TYPE:
                    print("Received invalid offer message.")
                    continue
                print(f"Received offer from {server_address[0]}, UDP port: {udp_port}, TCP port: {tcp_port}")
                return server_address[0], udp_port, tcp_port
            except Exception as e:
                print(f"Error receiving offer: {e}")

def send_udp_request(server_ip, udp_port, file_size):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_client:
        # Build the request message
        request_message = struct.pack('!IBQ', MAGIC_COOKIE, REQUEST_MESSAGE_TYPE, file_size)
        udp_client.sendto(request_message, (server_ip, udp_port))
        print(f"Sent UDP request to {server_ip}:{udp_port} for {file_size} bytes.")

        # Start receiving data
        received_packets = set()
        total_segments = None
        start_time = time.time()

        udp_client.settimeout(2)  # Timeout after 2 seconds of inactivity
        while True:
            try:
                data, addr = udp_client.recvfrom(2048)  # Buffer size larger than expected packet size
                magic_cookie, message_type, total_segments_received, sequence_number = struct.unpack('!IBQQ', data[:21])
                if magic_cookie != MAGIC_COOKIE or message_type != PAYLOAD_MESSAGE_TYPE:
                    print("Received invalid payload message.")
                    continue
                if total_segments is None:
                    total_segments = total_segments_received
                received_packets.add(sequence_number)
            except socket.timeout:
                print("No more data received. UDP transfer complete.")
                break
            except Exception as e:
                print(f"Error receiving UDP data: {e}")
                break

        end_time = time.time()
        total_time = end_time - start_time
        packets_received = len(received_packets)
        packet_loss = ((total_segments - packets_received) / total_segments) * 100 if total_segments else 0
        speed = (packets_received * 1024 * 8) / total_time  # Bits per second

        print(f"UDP transfer finished, total time: {total_time:.2f} seconds")
        print(f"Total speed: {speed / (1024 * 1024):.2f} Mbps")
        print(f"Percentage of packets received successfully: {100 - packet_loss:.2f}%")

def send_tcp_request(server_ip, tcp_port, file_size):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_client:
            tcp_client.connect((server_ip, tcp_port))
            print(f"Connected to server at {server_ip}:{tcp_port} via TCP")

            # Send file size request
            tcp_client.sendall(f"{file_size}\n".encode())
            print(f"Requested {file_size} bytes over TCP")

            # Measure time to receive data
            start_time = time.time()
            received_data = b""
            while len(received_data) < file_size:
                chunk = tcp_client.recv(4096)
                if not chunk:
                    break
                received_data += chunk
            end_time = time.time()

            # Print statistics
            total_time = end_time - start_time
            speed = (len(received_data) * 8) / total_time  # Bits per second
            print(f"TCP transfer finished, total time: {total_time:.2f} seconds")
            print(f"Total speed: {speed / (1024 * 1024):.2f} Mbps")
    except Exception as e:
        print(f"Error in TCP transfer: {e}")

if __name__ == "__main__":
    # Get user input
    file_size = int(input("Enter the file size in bytes: "))
    num_tcp_connections = int(input("Enter the number of TCP connections: "))
    num_udp_connections = int(input("Enter the number of UDP connections: "))

    while True:
        # Step 1: Listen for offers
        server_ip, udp_port, tcp_port = listen_for_offers()

        # Step 2: Start transfers
        print("Starting transfers...")
        threads = []

        # Start TCP transfers
        for i in range(num_tcp_connections):
            t = threading.Thread(target=send_tcp_request, args=(server_ip, tcp_port, file_size))
            threads.append(t)
            t.start()

        # Start UDP transfers
        for i in range(num_udp_connections):
            t = threading.Thread(target=send_udp_request, args=(server_ip, udp_port, file_size))
            threads.append(t)
            t.start()

        # Wait for all transfers to complete
        for t in threads:
            t.join()

        print("All transfers complete, listening for new offers...")
