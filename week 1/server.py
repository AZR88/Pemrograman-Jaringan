import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('127.0.0.1', 5000))
server_socket.listen(1)

print('Server listening on port 5000...')

while True:
    client_socket, client_address = server_socket.accept()
    print('Client connected:', client_address)

    while True:
        massage = client_socket.recv(1024).decode()
        if not massage:
            break  # If no message is received, break the loop

        print('Received message:', massage)

        response = input('Enter response: ')
        client_socket.send(response.encode())

    client_socket.close()  # Close the client socket after the conversation is over
    print('Client disconnected:', client_address)
