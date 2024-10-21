import socket
import threading
import time
import argparse


class Node:
    def __init__(self, name, data):
        self.name = name  # Book name
        self.data = data  # Line content
        self.next = None  # Next node in the shared list
        self.book_next = None  # Next node in the same book

class SharedList:
    def __init__(self):
        self.head = Node("head", None)  # Head of the list
        self.lock = threading.Lock()  # Lock to protect shared data
        self.book_heads = {}  # Keep track of the first node for each book

    def insert(self, name, data):
        new_node = Node(name, data)

        with self.lock:
            # Insert at the end of the shared list
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node

            # Update the book-specific linked list
            if name in self.book_heads:
                last_book_node = self.book_heads[name]
                while last_book_node.book_next:
                    last_book_node = last_book_node.book_next
                last_book_node.book_next = new_node
            else:
                self.book_heads[name] = new_node

            print(f"Added node: {data} (Book: {name})")

    def print_books(self):
        with self.lock:
            for book, head_node in self.book_heads.items():
                print(f"\nBook: {book}")
                current = head_node
                while current:
                    print(current.data)
                    current = current.book_next

shared_list = SharedList()

def handle_client(clientsocket, address, connection_id):
    print(f"Connection from {address} established.")
    current_book = None

    with clientsocket:
        while True:
            try:
                data = clientsocket.recv(1024).decode('utf-8')
                if not data:
                    break  # Exit if the client disconnects

                lines = data.splitlines()
                for line in lines:
                    if current_book is None:
                        # Assume the first line is the book title
                        current_book = line
                    else:
                        shared_list.insert(current_book, line)

            except ConnectionResetError:
                print(f"Connection with {address} lost.")
                break

    # Write the book to a file once the connection closes
    with open(f"book_{connection_id}.txt", 'w') as f:
        current = shared_list.book_heads.get(current_book, None)
        while current:
            f.write(current.data + '\n')
            current = current.book_next

    print(f"Connection {connection_id} from {address} closed.")

def analysis_thread(search_term, interval):
    while True:
        time.sleep(interval)
        with shared_list.lock:
            print(f"\n[Analysis Thread] Searching for: {search_term}")
            for book, head_node in shared_list.book_heads.items():
                count = 0
                current = head_node
                while current:
                    if search_term in current.data:
                        count += 1
                    current = current.book_next
                print(f"Book: {book} | '{search_term}' found {count} times.")

def main():

    parser = argparse.ArgumentParser(description="Multi-threaded network server")
    parser.add_argument("-l", "--listen", type=int, required=True, help="Port to listen on")
    parser.add_argument("-p", "--pattern", type=str, required=True, help="Search pattern for analysis")

    args = parser.parse_args()
    port = args.listen
    search_pattern = args.pattern

    host = socket.gethostname()

    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serversocket.bind((host, port))
    serversocket.listen(5)

    print(f"Server started on {host}:{port}")

    # Start analysis threads
    threading.Thread(target=analysis_thread, args=(search_pattern, 5), daemon=True).start()

    connection_id = 1
    while True:
        clientsocket, address = serversocket.accept()
        client_thread = threading.Thread(target=handle_client, args=(clientsocket, address, connection_id))
        client_thread.start()
        print(f"Started thread {client_thread.name} for {address}")
        connection_id += 1

if __name__ == "__main__":
    main()
