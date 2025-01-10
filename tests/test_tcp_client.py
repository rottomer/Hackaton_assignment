import socket
import time

# Configuration
SERVER_IP = "127.0.0.1"  # Change to the server's IP if running on a different machine
TCP_SERVER_PORT = 2026
FILE_SIZE = 1024 * 1024  # 1 MB

def test_tcp_client():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_client:
            tcp_client.connect((SERVER_IP, TCP_SERVER_PORT))
            print(f"Connected to server at {SERVER_IP}:{TCP_SERVER_PORT}")

            # Send file size request
            tcp_client.sendall(f"{FILE_SIZE}\n".encode())
            print(f"Requested {FILE_SIZE} bytes")

            # Measure time to receive data
            start_time = time.time()
            received_data = b""
            while len(received_data) < FILE_SIZE:
                chunk = tcp_client.recv(4096)  # Receive in chunks
                if not chunk:
                    break
                received_data += chunk
            end_time = time.time()

            # Print statistics
            total_time = end_time - start_time
            speed = FILE_SIZE / total_time  # Bytes per second
            print(f"Downloaded {len(received_data)} bytes in {total_time:.2f} seconds")
            print(f"Download speed: {speed / (1024 * 1024):.2f} MB/s")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_tcp_client()
