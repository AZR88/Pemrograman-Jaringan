import socket
import os

# Konfigurasi alamat dan port server
HOST = '127.0.0.1'
PORT = 80
BASE_DIR = "C:/Azriel/KULIAH/Pemrograman Jaringan/week 7/files"  # Pastikan path ini benar

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

    # Memeriksa jika permintaan adalah GET
    if method == 'GET':
        file_path = os.path.join(BASE_DIR, path.strip('/'))
        
        # Cek apakah file ada
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            
            # Cek apakah ada header Range dalam permintaan
            range_header = None
            for line in request.splitlines():
                if line.startswith("Range:"):
                    range_header = line
                    break
            
            # Jika ada permintaan Range, tangani permintaan Range
            if range_header:
                # Parsing rentang byte yang diminta
                range_value = range_header.split('=')[1]
                start_byte, end_byte = range_value.split('-')
                start_byte = int(start_byte)
                end_byte = int(end_byte) if end_byte else file_size - 1
                
                # Membatasi byte agar tidak melebihi ukuran file
                end_byte = min(end_byte, file_size - 1)
                content_length = end_byte - start_byte + 1
                
                # Mengirim header HTTP 206 Partial Content
                http_header = (
                    f"HTTP/1.1 206 Partial Content\r\n"
                    f"Content-Disposition: attachment; filename={os.path.basename(file_path)}\r\n"
                    f"Content-Range: bytes {start_byte}-{end_byte}/{file_size}\r\n"
                    f"Content-Length: {content_length}\r\n\r\n"
                )
                client_connection.sendall(http_header.encode('utf-8'))
                
                # Membuka file dan mengirim bagian yang diminta
                with open(file_path, 'rb') as file:
                    file.seek(start_byte)
                    bytes_to_send = end_byte - start_byte + 1
                    client_connection.sendfile(file, 0, bytes_to_send)
            else:
                # Jika tidak ada permintaan Range, kirim seluruh file (200 OK)
                http_header = (
                    f"HTTP/1.1 200 OK\r\n"
                    f"Content-Disposition: attachment; filename={os.path.basename(file_path)}\r\n"
                    f"Content-Length: {file_size}\r\n\r\n"
                )
                client_connection.sendall(http_header.encode('utf-8'))
                
                # Membuka dan mengirim seluruh konten file
                with open(file_path, 'rb') as file:
                    client_connection.sendfile(file)
        else:
            # Jika file tidak ditemukan
            http_response = "HTTP/1.1 404 Not Found\r\n\r\nFile tidak ditemukan"
            client_connection.sendall(http_response.encode('utf-8'))
    
    else:
        # Jika metode selain GET digunakan
        http_response = "HTTP/1.1 405 Method Not Allowed\r\n\r\nMetode tidak didukung"
        client_connection.sendall(http_response.encode('utf-8'))
    
    # Menutup koneksi
    client_connection.close()
