import socket

def send_udp_requests():
    udp_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    requests = ['request1', 'fail', 'request2']
    
    for request in requests:
        udp_client.sendto(request.encode(), ('localhost', 65433))
        data, _ = udp_client.recvfrom(1024)
        print(f"UDP Response: {data.decode()}")
    
    udp_client.close()

if __name__ == "__main__":
    send_udp_requests()
