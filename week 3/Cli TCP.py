import socket

def send_tcp_requests():
    tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_client.connect(('localhost', 65432))
    
    requests = ['request1', 'request2', 'fail', 'request3']
    
    for request in requests:
        response = ""
        attempt = 0
        
        while "failed" in response or attempt == 0:  # Kirim ulang jika ada "failed" di respons
            attempt += 1
            print(f"Sending request: {request}, Attempt: {attempt}")
            tcp_client.sendall(request.encode())
            response = tcp_client.recv(1024).decode()
            print(f"TCP Response: {response}")
            
            if attempt >= 3:  # Maksimal 3 kali mencoba jika gagal
                print(f"Request '{request}' failed after {attempt} attempts.")
                break
    
    tcp_client.close()

if __name__ == "__main__":
    send_tcp_requests()
