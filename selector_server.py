import selectors
import socket

# Create a default selector that will manage multiple socket connections
sel = selectors.DefaultSelector()

# Function to accept a connection and register it for reading
def accept(sock):
    conn, addr = sock.accept()  # Accept the connection
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)  # Set non-blocking mode
    # Register the connection socket to be monitored for read events
    sel.register(conn, selectors.EVENT_READ, read)

# Function to handle reading from a client socket
def read(conn):
    data = conn.recv(1024)  # Read data from the socket
    if data:
        print(f"Received data: {data} from {conn}")
        conn.sendall(data)  # Echo back the data
    else:
        print(f"Closing connection to {conn}")
        sel.unregister(conn)  # Unregister the socket from the selector
        conn.close()  # Close the connection

# Set up the server socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('localhost', 65432))  # Bind to localhost on port 65432
sock.listen()
sock.setblocking(False)  # Set non-blocking mode

# Register the server socket to be monitored for incoming connections
sel.register(sock, selectors.EVENT_READ, accept)

print("Server started, waiting for connections...")

try:
    while True:
        # Wait for events (blocking until there are any)
        events = sel.select()
        for key, mask in events:
            print(f"key:{key},mask:{mask}")
            callback = key.data  # Get the callback function (accept or read)
            callback(key.fileobj)  # Call the function with the socket object
finally:
    print("Shutting down the server...")
    sel.close()  # Close the selector
    sock.close()  # Close the server socket

