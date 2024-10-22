import socket
import ssl
import threading
from urllib.parse import urlparse

# Fungsi untuk membuat permintaan HTTP menggunakan socket
def download_part_via_socket(host, path, port, start, end, part_file, is_https=False):
    request_header = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"Range: bytes={start}-{end}\r\n"
        f"Connection: close\r\n\r\n"
    )
    
    # Menggunakan socket dengan atau tanpa SSL tergantung protokol
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        if is_https:
            context = ssl.create_default_context()  # Membuat konteks SSL
            sock = context.wrap_socket(sock, server_hostname=host)  # Membungkus socket dengan SSL
        sock.connect((host, port))
        sock.sendall(request_header.encode())
        
        response = b''
        while True:
            chunk = sock.recv(1024)
            if not chunk:
                break
            response += chunk
    
    # Memisahkan header HTTP dan konten
    header_end = response.find(b'\r\n\r\n') + 4
    body = response[header_end:]
    
    # Menyimpan file dalam mode binary
    with open(part_file, 'wb') as f:
        f.write(body)

# Fungsi untuk menggabungkan file part menjadi satu file
def merge_files(output_file, parts):
    with open(output_file, 'wb') as merged_file:
        for part_file in parts:
            with open(part_file, 'rb') as part:
                merged_file.write(part.read())

# Fungsi untuk mendownload file secara paralel
def parallel_download_via_socket(url, output_file, num_threads=4):
    # Parse URL
    parsed_url = urlparse(url)
    host = parsed_url.hostname
    path = parsed_url.path
    is_https = parsed_url.scheme == 'https'
    port = 443 if is_https else 80
    
    # Membuat permintaan HEAD untuk mendapatkan ukuran file
    request_header = (
        f"HEAD {path} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"Connection: close\r\n\r\n"
    )
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        if is_https:
            context = ssl.create_default_context()  # Membuat konteks SSL untuk HTTPS
            sock = context.wrap_socket(sock, server_hostname=host)  # Membungkus socket dengan SSL
        sock.connect((host, port))
        sock.sendall(request_header.encode())
        
        response = b''
        while True:
            chunk = sock.recv(1024)
            if not chunk:
                break
            response += chunk

    # Mencari ukuran file dari response header
    headers = response.decode().split('\r\n')
    for header in headers:
        print(header)  # Untuk debug, mencetak semua header

    content_length = next((int(header.split(': ')[1]) for header in headers if 'Content-Length' in header), None)

    if content_length is None:
        raise ValueError("Content-Length tidak ditemukan dalam header.")

    # Menghitung ukuran tiap bagian
    part_size = content_length // num_threads
    threads = []
    part_files = []

    # Mulai download setiap bagian file secara paralel
    for i in range(num_threads):
        start = i * part_size
        end = (start + part_size - 1) if i < num_threads - 1 else content_length - 1
        part_file = f'part_{i}.tmp'
        part_files.append(part_file)
        
        # Log untuk melihat rentang byte
        print(f"Downloading part {i}: bytes {start}-{end}")
        
        # Buat dan mulai thread untuk mendownload bagian file
        thread = threading.Thread(target=download_part_via_socket, args=(host, path, port, start, end, part_file, is_https))
        threads.append(thread)
        thread.start()

    # Tunggu hingga semua thread selesai
    for thread in threads:
        thread.join()

    # Gabungkan semua file part menjadi satu file utuh
    merge_files(output_file, part_files)

# Contoh penggunaan
if __name__ == '__main__':
    file_url = "https://unej.ac.id/wp-content/uploads/2023/05/Final-Penulisan-Tugas-Akhir-UNEJ-2022-6-Maret-2023.pdf"  # URL file PDF
    output_filename = "final_penulisan.pdf"
    
    parallel_download_via_socket(file_url, output_filename, num_threads=4)
    print(f"Download selesai. File disimpan sebagai {output_filename}")
