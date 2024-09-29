import socket

def handle_tcp(conn, addr):
    print(f"TCP connection from {addr}")
    while True:
        data = conn.recv(1024).decode()
        if not data:
            break
        print(f"TCP Received: {data}")
        if data == "fail":
            response = "TCP Request failed!"
        else:
            response = f"TCP Request '{data}' succeeded!"
        conn.sendall(response.encode())
    conn.close()

def start_tcp_server():
    tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_server.bind(('localhost', 65432))
    tcp_server.listen()
    
    print("TCP Server is listening on port 65432...")
    
    while True:
        conn, addr = tcp_server.accept()
        handle_tcp(conn, addr)

if __name__ == "__main__":
    start_tcp_server()
