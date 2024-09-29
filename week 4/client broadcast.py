import socket
import threading

# Fungsi untuk menerima pesan dari server
def receive_messages(sock):
    while True:
        try:
            message = sock.recv(1024).decode()
            if message:
                print(f"Message from other user: {message}")
        except:
            print("Connection to server lost")
            sock.close()
            break

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('192.168.243.140', 2037)  # Alamat server
    client.connect(server_address)
    
    # Membuat thread untuk menerima pesan dari server
    receive_thread = threading.Thread(target=receive_messages, args=(client,))
    receive_thread.start()

    # Mengirim pesan ke server
    while True:
        message = input("You: ")
        client.send(message.encode())

if __name__ == "__main__":
    main()
