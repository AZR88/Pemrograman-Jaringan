import socket

def send_request(method, path, body=None):
    HOST = '127.0.0.1'
    PORT = 8080

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    if method == 'GET' or method == 'DELETE':
        request = f"{method} {path} HTTP/1.1\r\nHost: {HOST}\r\n\r\n"
    elif method == 'PUT':
        request = f"{method} {path} HTTP/1.1\r\nHost: {HOST}\r\n\r\n{body}"

    client_socket.sendall(request.encode('utf-8'))

    # Menerima respon dari server
    response = client_socket.recv(1024).decode('utf-8')
    print(f"Response dari server:\n{response}")
    
    # Menutup koneksi
    client_socket.close()

# Contoh permintaan GET, PUT, DELETE
send_request('PUT', '/data1', 'Ini adalah data pertama')
send_request('GET', '/data1')
send_request('DELETE', '/data1')
send_request('GET', '/data1')
