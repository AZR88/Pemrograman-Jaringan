import socket

def start_client(client_name):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 2037))
    
    # Kirim nama client
    client_socket.sendall(client_name.encode('utf-8'))
    
    # Terima balasan dari server
    data = client_socket.recv(1024)
    print(f"Received from server: {data.decode('utf-8')}")
    
    client_socket.close()

if __name__ == '__main__':
    start_client('client 1')  
