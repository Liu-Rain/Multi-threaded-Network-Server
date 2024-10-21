#!/usr/bin/env python3
import socket
import threading
import argparse
import sys
import os
from collections import defaultdict
import time

class Node:
    def __init__(self, line, book_id):
        self.line = line
        self.book_id = book_id
        self.next = None
        self.book_next = None
        self.next_frequent_search = None

class SharedData:
    def __init__(self):
        self.head = None
        self.tail = None
        self.book_heads = {}
        self.book_tails = {}
        self.lock = threading.Lock()
        self.book_count = 0
        self.book_count_lock = threading.Lock()

shared_data = SharedData()
search_pattern = ""
analysis_lock = threading.Lock()
last_analysis_time = 0

def add_node(line, book_id):
    global shared_data
    node = Node(line, book_id)
    with shared_data.lock:
        if shared_data.head is None:
            shared_data.head = node
            shared_data.tail = node
        else:
            shared_data.tail.next = node
            shared_data.tail = node
        if book_id not in shared_data.book_heads:
            shared_data.book_heads[book_id] = node
            shared_data.book_tails[book_id] = node
        else:
            shared_data.book_tails[book_id].book_next = node
            shared_data.book_tails[book_id] = node
    print(f"Added node to shared list: Book ID {book_id}, Line: {line.strip()}")

def handle_client(conn, addr, book_number):
    global shared_data
    book_id = book_number
    book_title = None
    try:
        with conn:
            buffer = ""
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                buffer += data.decode('utf-8')
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if book_title is None:
                        book_title = line.strip()
                        add_node(book_title, book_id)
                    else:
                        add_node(line.strip(), book_id)
    except Exception as e:
        print(f"Error handling client {addr}: {e}")
    finally:
        write_book_to_file(book_id)
        print(f"Connection from {addr} closed.")

def write_book_to_file(book_id):
    global shared_data
    filename = f"book_{book_id:02d}.txt"
    with shared_data.lock:
        if book_id not in shared_data.book_heads:
            print(f"No data for book ID {book_id}.")
            return
        current = shared_data.book_heads[book_id]
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            while current:
                f.write(current.line + '\n')
                current = current.book_next
        print(f"Wrote book to {filename}.")
    except Exception as e:
        print(f"Error writing book {filename}: {e}")

def analysis_thread_func(interval, pattern):
    global shared_data, last_analysis_time
    while True:
        time.sleep(interval)
        with analysis_lock:
            current_time = time.time()
            if current_time - last_analysis_time < interval:
                continue
            last_analysis_time = current_time
        book_counts = defaultdict(int)
        with shared_data.lock:
            current = shared_data.head
            while current:
                if pattern in current.line:
                    book_counts[current.book_id] += 1
                current = current.next
        book_titles = {}
        with shared_data.lock:
            for book_id, head_node in shared_data.book_heads.items():
                book_titles[book_id] = head_node.line
        sorted_books = sorted(book_counts.items(), key=lambda x: x[1], reverse=True)
        output_lines = []
        for book_id, count in sorted_books:
            title = book_titles.get(book_id, f"Book {book_id}")
            output_lines.append(f"{title}: {count}")
        print("\n--- Analysis Report ---")
        for line in output_lines:
            print(line)
        print("--- End of Report ---\n")

def start_server(listen_port, pattern):
    global search_pattern
    search_pattern = pattern
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', listen_port))
        s.listen()
        print(f"Server listening on port {listen_port}...")
        while True:
            conn, addr = s.accept()
            with shared_data.book_count_lock:
                shared_data.book_count += 1
                book_number = shared_data.book_count
            print(f"Accepted connection from {addr}, assigned Book ID {book_number}.")
            client_thread = threading.Thread(target=handle_client, args=(conn, addr, book_number))
            client_thread.daemon = True
            client_thread.start()

def main():
    parser = argparse.ArgumentParser(description="Multi-Threaded Network Server for Pattern Analysis")
    parser.add_argument('-l', '--listen', type=int, required=True, help='Listening port (>1024)')
    parser.add_argument('-p', '--pattern', type=str, required=True, help='Search pattern')
    parser.add_argument('-i', '--interval', type=int, default=5, help='Analysis interval in seconds (default: 5)')
    args = parser.parse_args()
    if args.listen <= 1024:
        print("Please choose a port number greater than 1024.")
        sys.exit(1)
    num_analysis_threads = 2
    for _ in range(num_analysis_threads):
        t = threading.Thread(target=analysis_thread_func, args=(args.interval, args.pattern))
        t.daemon = True
        t.start()
    try:
        start_server(args.listen, args.pattern)
    except KeyboardInterrupt:
        print("\nServer shutting down.")
        sys.exit(0)

if __name__ == "__main__":
    main()