import socket

# Konfigurasi alamat dan port server
HOST = '127.0.0.1'
PORT = 80

# Nama file yang ingin diminta dari server
file_name = "demo.pdf"  # Ganti dengan nama file yang tersedia di server

# Rentang byte yang akan diminta dalam satu kali permintaan
start_byte = 100
end_byte = 700 # Mengunduh byte dari 10 hingga 15

# Membuat socket client
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Menghubungkan ke server
client_socket.connect((HOST, PORT))

# Membuat permintaan GET HTTP dengan header Range
request = (
    f"GET /{file_name} HTTP/1.1\r\n"
    f"Host: {HOST}\r\n"
    f"Range: bytes={start_byte}-{end_byte}\r\n"  # Meminta byte dalam rentang tertentu
    "\r\n"
)

# Mengirim permintaan ke server
client_socket.sendall(request.encode('utf-8'))

# Buffer untuk menyimpan respons
response = b""

# Menerima respons hingga header HTTP selesai
while b"\r\n\r\n" not in response:
    chunk = client_socket.recv(1024)
    if not chunk:
        break
    response += chunk

# Cetak seluruh respons untuk debugging
print(f"Response diterima (untuk debugging):\n{response.decode('utf-8', errors='replace')}\n")

# Cek apakah ada pemisah \r\n\r\n
if b"\r\n\r\n" in response:
    # Memisahkan header dan sisa konten
    header, content = response.split(b'\r\n\r\n', 1)
    print(f"Header diterima:\n{header.decode('utf-8')}\n")

    # Mengecek apakah respons adalah 206 Partial Content (sukses untuk Range)
    if b"206 Partial Content" in header:
        # Tentukan lokasi dan nama file yang akan disimpan
        file_path = f"downloaded_{file_name}"
        
        # Membuka file untuk menyimpan data yang diterima
        with open(file_path, 'wb') as file:  # Mode 'wb' untuk menulis file baru
            # Menyimpan bagian konten yang sudah diterima
            file.write(content)
            
            # Menerima sisa konten file dalam potongan-potongan sesuai range
            while True:
                chunk = client_socket.recv(1024)
                if not chunk:
                    break
                file.write(chunk)
        
        print(f"File '{file_name}' berhasil diunduh (byte {start_byte} hingga {end_byte}) dan disimpan sebagai '{file_path}'.")
    else:
        print("File tidak ditemukan atau terjadi kesalahan.")
else:
    print("Header HTTP tidak lengkap atau tidak ditemukan.")

# Menutup koneksi
client_socket.close()
