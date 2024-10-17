import socket



# create an INET, STREAMing socket
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind the socket to a public host, and a well-known port
serversocket.bind((socket.gethostname(), 12345))
# become a server socket
serversocket.listen(5)



while True:
    # accept connections from outside
    (clientsocket, address) = serversocket.accept()

    data = clientsocket.recv(1024)  # Buffer size of 1024 bytes
    if data:
        print(f"Received data: {data.decode('utf-8')}")

    # now do something with the clientsocket
    # in this case, we'll pretend this is a threaded server
    print(f"Connection from {address} has been established.")

    # Send a welcome message to the client
    clientsocket.send(b"Welcome to the server!\n")
