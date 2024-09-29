import socket
import threading

clients = []  # List untuk menyimpan client yang terhubung

# Fungsi untuk menangani setiap client
def handle_client(client_socket, client_address):
    print(f"New connection from {client_address}")
    while True:
        try:
            message = client_socket.recv(1024)
            if not message:
                break
            print(f"Received from {client_address}: {message.decode()}")
            broadcast(message, client_socket)
        except:
            clients.remove(client_socket)
            break
    client_socket.close()

# Fungsi untuk menyebarkan pesan ke semua client
def broadcast(message, sender_socket):
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message)
            except:
                clients.remove(client)

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('192.168.243.140', 2037))  # Mengikat ke semua alamat yang tersedia pada port 5002
    server.listen(5)
    print("Server started and listening for connections...")

    while True:
        client_socket, client_address = server.accept()
        clients.append(client_socket)  # Menambahkan client yang baru terhubung
        thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        thread.start()

if __name__ == "__main__":
    main()
