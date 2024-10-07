import socket

# Konfigurasi alamat dan port server
HOST = '127.0.0.1'  # Alamat localhost
PORT = 8080         # Port server

data_store = {}  # Tempat penyimpanan data sederhana di server

# Membuat socket server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print(f"Server berjalan di {HOST}:{PORT}...")

while True:
    # Menerima koneksi dari client
    client_connection, client_address = server_socket.accept()
    
    # Menerima permintaan HTTP dari client
    request = client_connection.recv(1024).decode('utf-8')
    print(f"Permintaan diterima:\n{request}")
    
    # Memisahkan permintaan HTTP menjadi metode dan path
    request_line = request.splitlines()[0]
    method, path, _ = request_line.split()

    # Menangani metode HTTP
    if method == 'GET':
        response_body = data_store.get(path, "Data tidak ditemukan")
        http_response = f"HTTP/1.1 200 OK\n\n{response_body}"
    
    elif method == 'PUT':
        # Simpan data yang dikirim dalam body
        data_store[path] = request.split("\n\n")[1]
        http_response = "HTTP/1.1 200 OK\n\nData berhasil disimpan"
    
    elif method == 'DELETE':
        if path in data_store:
            del data_store[path]
            http_response = "HTTP/1.1 200 OK\n\nData berhasil dihapus"
        else:
            http_response = "HTTP/1.1 404 Not Found\n\nData tidak ditemukan"
    
    else:
        # Jika metode tidak dikenali
        http_response = "HTTP/1.1 405 Method Not Allowed\n\nMetode tidak didukung"
    
    # Mengirim respon HTTP ke client
    client_connection.sendall(http_response.encode('utf-8'))
    
    # Menutup koneksi
    client_connection.close()
