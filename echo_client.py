import socket

def start_echo_client(host='127.0.0.1', port=65432, message="Hello, Server!"):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))
        client_socket.sendall(message.encode())
        data = client_socket.recv(1024)
    
    print(f"Received from server: {data.decode()}")

if __name__ == "__main__":
    start_echo_client()

