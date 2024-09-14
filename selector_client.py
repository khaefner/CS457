import socket

def main():
    # Define server address and port
    server_address = ('localhost', 65432)
    
    # Create a TCP/IP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # Connect to the server
        sock.connect(server_address)
        print("Connected to the server.")
        
        try:
            # Send data to the server
            message = "Hello, Server!".encode('utf-8')
            print(f"Sending: {message}")
            sock.sendall(message)
            
            # Wait for response and read data
            data = sock.recv(1024)
            print(f"Received: {data.decode('utf-8')}")
        
        finally:
            print("Closing the connection.")
            sock.close()

if __name__ == "__main__":
    main()

