import socket
import time

def start_client(client_name):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('127.0.0.1', 2037))
        
        for i in range(20):
            message = f"{client_name} message {i + 1}"
            
            try:
                # Kirim pesan ke server
                client_socket.sendall(message.encode('utf-8'))
                print(f"Sent: {message}")
                
                # Terima respon dari server
                data = client_socket.recv(1024)
                print(f"Received from server: {data.decode('utf-8')}")
                
                # Jeda 1 detik sebelum mengirim pesan berikutnya
                time.sleep(1)
            
            except socket.error as e:
                print(f"Socket error during send/receive: {e}")
                break  # Keluar dari loop jika terjadi error

    except socket.error as e:
        print(f"Error creating or connecting socket: {e}")
    
    finally:
        # Tutup socket setelah semua pesan dikirim
        try:
            client_socket.close()
            print("Socket closed.")
        except NameError:
            print("Socket was not created.")

if __name__ == '__main__':
    start_client('client 2')
