import socket
import threading

# Function to handle a client connection
def handle_client(clientsocket, address):
    print(f"Connection from {address} has been established.")
    
    while True:
        try:
            # Receive data from the client
            data = clientsocket.recv(1024)  # Buffer size of 1024 bytes
            
            if not data:
                print(f"Connection from {address} closed.")
                break  # Exit if the client disconnects
            
            # Print the received data
            print(f"Received from {address}: {data.decode('utf-8')}")
            
            # Send a response to the client
            clientsocket.send(b"Data received!\n")

        except ConnectionResetError:
            print(f"Connection with {address} lost.")
            break

    clientsocket.close()

# Create a socket object
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Allow the address/port to be reused
serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind the socket to the host and port
host = socket.gethostname()  # or '0.0.0.0' for all available interfaces
port = 12345
serversocket.bind((host, port))

print(f"Server started on {host}:{port}")

# Start listening for incoming connections
serversocket.listen(5)

while True:
    # Accept an incoming connection
    clientsocket, address = serversocket.accept()

    # Create a new thread to handle the client connection
    client_thread = threading.Thread(target=handle_client, args=(clientsocket, address))
    client_thread.start()

    print(f"Started thread {client_thread.name} for {address}")
