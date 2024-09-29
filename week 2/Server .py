import socket

def main():
    # Membuat socket untuk server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    server_IP = '192.168.71.140'
    server_PORT = 2037
    server_socket.bind((server_IP, server_PORT))
    server_socket.listen(1)
    
    print(f'Server is listening on {server_IP}:{server_PORT}')

    try:
        # Menerima koneksi dari client
        conn, addr = server_socket.accept() # Menunggu koneksi
        print(f'Connected by {addr}')

        # Menerima data dari client
        buffer_size = 5
        data = ""
        while True:
            part = conn.recv(buffer_size).decode()  # Menerima bagian kecil dari data
            if not part:  # Jika tidak ada data lagi dari client, keluar dari loop
                break
            data += part
            print(f"Received part: {part}")

        print(f"Full message received ({len(data)}  characters): {data}")  # Menampilkan panjang dan keseluruhan pesan

        # Mengirimkan respons ke client
        response = f"pesan yang anda kirim adalah : {data}\n denganpanjang pesan : {len(data)}"
        conn.sendall(response.encode())  # Mengirimkan seluruh respons sekaligus

        print("Response sent.")
        
    except socket.error as e:
        print(f"Socket error: {e}")

    finally:
        # Menutup koneksi dengan client
        conn.close()
        server_socket.close()

if __name__ == "__main__":
    main()
