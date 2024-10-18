import socket
import threading

class Node:
    def __init__(self, name, data):
        self.name = name
        self.data = data
        self.next = None
        self.book_next = None

class Share_list:
    def __init__(self):
        self.head = Node("head","head")
    
    def print_book(self):
        finish = []
        current = self.head.next
        finish.append(current)

        while current != None:

            if current.name not in finish:
                current_read = current

                while current_read != None:
                    print(current_read.data)
                    current_read = current_read.book_next

                finish.append(current.name)
            current = current.next
    def get_head(self):
        return self.head
    def insert(self, name, data):
        new_node = Node(name, data)
        book = {}

        current_node = self.head
        while(current_node.next):
            current_node = current_node.next
            
            book.update({current_node.name:current_node}) 
        
        current_node.next = new_node
        book[name] = new_node
        print(book)
    
            
        
        
x = Share_list()
x.insert("book1", "dwadas")
x.insert("book2", "dwadas")
x.insert("book3", "dwadas")
x.insert("book1", "dwadas")
x.insert("book2", "dwadas")
x.insert("book3", "dwadas")


    



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
            #print(f"Received from {address}: {data.decode('utf-8')}")
            
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

node_array = []

while True:
    # Accept an incoming connection
    clientsocket, address = serversocket.accept()

    # Create a new thread to handle the client connection
    client_thread = threading.Thread(target=handle_client, args=(clientsocket, address))
    client_thread.start()
    if client_thread.name not in node_array:
        node_array.append(client_thread.name)

    print(f"Started thread {client_thread.name} for {address}")
    print(node_array)
