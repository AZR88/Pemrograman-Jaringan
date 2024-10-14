import socket
import os

# Konfigurasi alamat dan port server
HOST = '127.0.0.1'  # Alamat localhost
PORT = 8080         # Port server
BASE_DIR = "./files"  # Direktori tempat file berada

# Membuat socket server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print(f"Server berjalan di {HOST}:{PORT}...")

while True:
    # Menerima koneksi dari client
    client_connection, client_address = server_socket.accept()
    
    # Menerima permintaan HTTP dari client (browser)
    request = client_connection.recv(1024).decode('utf-8')
    print(f"Permintaan diterima:\n{request}")
    
    # Memisahkan permintaan HTTP menjadi metode dan path
    request_line = request.splitlines()[0]
    method, path, _ = request_line.split()

    # Menangani permintaan GET untuk file
    if method == 'GET':
        file_path = os.path.join(BASE_DIR, path.strip('/'))
        
        # Cek apakah file ada
        if os.path.exists(file_path):
            # Mengambil ukuran file
            file_size = os.path.getsize(file_path)
            
            # Membuat header HTTP 200 OK dengan informasi tentang file
            http_header = f"HTTP/1.1 200 OK\n"
            http_header += f"Content-Disposition: attachment; filename={os.path.basename(file_path)}\n"
            http_header += f"Content-Length: {file_size}\n\n"
            
            # Mengirim header ke client
            client_connection.sendall(http_header.encode('utf-8'))
            
            # Membuka dan mengirim konten file
            with open(file_path, 'rb') as file:
                client_connection.sendfile(file)
        else:
            # Jika file tidak ditemukan
            http_response = "HTTP/1.1 404 Not Found\n\nFile tidak ditemukan"
            client_connection.sendall(http_response.encode('utf-8'))
    
    else:
        # Jika metode selain GET digunakan
        http_response = "HTTP/1.1 405 Method Not Allowed\n\nMetode tidak didukung"
        client_connection.sendall(http_response.encode('utf-8'))
    
    # Menutup koneksi
    client_connection.close()
