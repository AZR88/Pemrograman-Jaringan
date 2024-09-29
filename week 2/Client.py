import socket

def main():
    # Membuat socket untuk client
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    server_IP = '127.0.0.1'
    server_PORT = 5000

    try:
        # Koneksi ke server
        client_socket.connect((server_IP, server_PORT))
        print(f'Client connected to {server_IP}:{server_PORT}')
        
        # Membuat pesan dengan 1000 karakter 'A'
        message = 'A' * 1000
        print("Sending message...")

        # Mengirim pesan ke server
        client_socket.sendall(message.encode())  # Menggunakan sendall untuk memastikan seluruh data dikirim

        print("Message sent.")
        client_socket.shutdown(socket.SHUT_WR)
        # Menerima respons dari server dengan buffer size kecil (5 byte per potongan)
        buffer_size = 5
        response = ""
        while True:
            part = client_socket.recv(buffer_size).decode()  # Menerima sebagian data
            if not part:  # Jika tidak ada data lagi, keluar dari loop
                break
            response += part

            

        print("Server response:", response)

    except socket.error as e:
        print(f"Socket  error: {e}")

    finally:
        # Menutup koneksi setelah menerima semua data dari server
        client_socket.close()

if __name__ == "__main__":
    main()
