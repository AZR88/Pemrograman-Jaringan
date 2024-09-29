import socket

def handle_udp(udp_server):
    while True:
        data, addr = udp_server.recvfrom(1024)
        print(f"UDP Received from {addr}: {data.decode()}")
        if data.decode() == "fail":
            response = "UDP Request failed!"
        else:
            response = f"UDP Request '{data.decode()}' succeeded!"
        udp_server.sendto(response.encode(), addr)

def start_udp_server():
    udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_server.bind(('localhost', 65433))
    
    print("UDP Server is listening on port 65433...")
    handle_udp(udp_server)

if __name__ == "__main__":
    start_udp_server()
