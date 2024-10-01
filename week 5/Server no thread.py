import socket
import time

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', 2037))
    server_socket.listen(5)
    print("Server started. Waiting for clients...")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Client {client_address} connected.")
        
        data = client_socket.recv(1024)
        print(f"Received data from {client_address}: {data.decode('utf-8')}")
        
        # Simulate long processing time for client 1
        if data.decode('utf-8') == 'client 1':
            print("Processing large data from client 1...")
            time.sleep(20)  #delay

        client_socket.sendall(b"Hello, Client!")
        client_socket.close()

if __name__ == '__main__':
    start_server()
