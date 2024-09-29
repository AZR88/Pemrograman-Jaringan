import socket
import threading

def handle_client(client_socket, client_address):
    print(f"Client {client_address} connected.")
    data = client_socket.recv(1024)
    print(f"Received data from {client_address}: {data.decode('utf-8')}")
    
    # Simulate long processing time for client 1
    if data.decode('utf-8') == 'client 1':
        print("Processing large data from client 1...")
        import time
        time.sleep(10)  # Simulate delay
    
    client_socket.sendall(b'Hello, client!')
    client_socket.close()

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', 2037))
    server_socket.listen(5)
    print("Server started. Waiting for clients.....")

    while True:
        client_socket, client_address = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()

if __name__ == '__main__':
    start_server()
 