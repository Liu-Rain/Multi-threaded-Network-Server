import socket
import threading

class Node:
    

    def __init__(self, name, data):
        self.name = name
        self.data = data
        self.next = None
        self.book_next = None
    

class Share_list:
    book = {}
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
                    print(current_read.name)
                    current_read = current_read.book_next

                finish.append(current.name)
            current = current.next
    def get_head(self):
        return self.head
    
    def insert(self, name, data):
        #set next = newnode
        new_node = Node(name, data)
        current_node = self.head
        while(current_node.next):
            current_node = current_node.next
        current_node.next = new_node


        #set book_next = newnode
        if name in self.book:
            self.book[name].book_next = new_node
        else:
            self.book.update({new_node.name: new_node})





    
            
        
        
x = Share_list()
x.insert("book1", "dwadas")
x.insert("book2", "dwadas")
x.insert("book3", "dwadas")
x.insert("book1", "biik1")
x.insert("book2", "book222")
x.insert("book3", "bolk3")

    



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


while True:
    # Accept an incoming connection
    clientsocket, address = serversocket.accept()

    # Create a new thread to handle the client connection
    client_thread = threading.Thread(target=handle_client, args=(clientsocket, address))

    client_thread.start()


    print(f"Started thread {client_thread.name} for {address}")
