import socket

def send_request(method, path, body=None):
    HOST = '127.0.0.1'  # Ganti dengan IP server jika diperlukan
    PORT = 80           # Port default untuk HTTP

    # Membuat socket untuk koneksi TCP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    # Membuat request berdasarkan metode
    if method == 'GET' or method == 'DELETE':
        request = f"{method} {path} HTTP/1.1\r\nHost: {HOST}\r\nConnection: close\r\n\r\n"
    elif method == 'PUT':
        content_length = len(body) if body else 0
        request = (
            f"{method} {path} HTTP/1.1\r\n"
            f"Host: {HOST}\r\n"
            f"Content-Length: {content_length}\r\n"
            f"Connection: close\r\n\r\n"
            f"{body if body else ''}"
        )

    # Mengirim request HTTP ke server
    client_socket.sendall(request.encode('utf-8'))

    # Menerima respon dari server
    response = ""
    while True:
        data = client_socket.recv(1024)
        if not data:
            break
        response += data.decode('utf-8')

    # Menampilkan respon dari server
    print(f"Response dari server:\n{response}")

    # Menutup koneksi
    client_socket.close()

# Contoh permintaan GET ke file yang ada
send_request('GET', '/index.html')
