import socket
import threading

def handle_client(client_socket, client_address):
    try:
        print(f"Client {client_address} connected.")

        # Server terus mendengarkan pesan dari client sampai client menutup koneksi
        while True:
            data = client_socket.recv(1024)
            if not data:
                print(f"Client {client_address} disconnected.")
                break  # Keluar dari loop jika client memutuskan koneksi
            
            client_message = data.decode('utf-8')
            print(f"Received from {client_address}: {client_message}")

            # Kirim balasan ke client
            response = f"Server received: {client_message}"
            client_socket.sendall(response.encode('utf-8'))
            
    except socket.error as e:
        print(f"Socket error: {e}")
    
    finally:
        # Tutup koneksi jika selesai atau ada error
        client_socket.close()
        print(f"Connection with {client_address} closed.")

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', 2037))
    server_socket.listen(5)
    print("Server started. Waiting for clients...")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Accepted connection from {client_address}")

        # Mulai thread baru untuk setiap client
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()

if __name__ == '__main__':
    start_server()
