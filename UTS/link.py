import socket
import threading
import time
from datetime import datetime

# Fungsi untuk membuat permintaan HTTP menggunakan socket
def send_request(method, host, port, path, range_header=None, body=None):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))

        request = f"{method} {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n"
        if range_header:
            request += f"Range: {range_header}\r\n"
        if body:
            content_length = len(body)
            request += f"Content-Length: {content_length}\r\n\r\n{body}"
        else:
            request += "\r\n"

        sock.sendall(request.encode())

        response = b''
        while True:
            chunk = sock.recv(1024)
            if not chunk:
                break
            response += chunk

    return response

# Fungsi untuk download bagian file menggunakan fungsi send_request
def download_part_via_socket(host, port, path, start, end, part_file):
    range_header = f"bytes={start}-{end}"
    response = send_request('GET', host, port, path, range_header)

    header_end = response.find(b'\r\n\r\n') + 4
    body = response[header_end:]
    
    total_size = end - start + 1
    downloaded_size = 0

    # Simpan bagian file dalam mode binary dengan progress
    with open(part_file, 'wb') as f:
        f.write(body)
        downloaded_size += len(body)
        percent_complete = (downloaded_size / total_size) * 100
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] Part {part_file}: {percent_complete:.2f}% downloaded.")

def merge_files(output_file, parts):
    with open(output_file, 'wb') as merged_file:
        for part_file in parts:
            with open(part_file, 'rb') as part:
                merged_file.write(part.read())

def parallel_download_via_socket(host, port, path, output_file, num_threads=4):
    response = send_request('HEAD', host, port, path)
    headers = response.decode().split('\r\n')
    content_length = next((int(header.split(': ')[1]) for header in headers if 'Content-Length' in header), None)

    if content_length is None:
        raise ValueError("Content-Length tidak ditemukan dalam header.")

    part_size = content_length // num_threads
    threads = []
    part_files = []

    for i in range(num_threads):
        start = i * part_size
        end = (start + part_size - 1) if i < num_threads - 1 else content_length - 1
        part_file = f'part_{i}.tmp'
        part_files.append(part_file)
        
        print(f"Downloading part {i}: bytes {start}-{end}")
        
        thread = threading.Thread(target=download_part_via_socket, args=(host, port, path, start, end, part_file))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    merge_files(output_file, part_files)

# Contoh penggunaan
if __name__ == '__main__':
    host = "127.0.0.1"  # IP address lokal
    port = 80           # Port HTTP
    path = "/PemrogramanJaringan/VALORANT%20%20%202023-08-16%2021-55-13.mp4"
    output_filename = "video.mp4"
    
    parallel_download_via_socket(host, port, path, output_filename, num_threads=4)
    print(f"Download selesai. File disimpan sebagai {output_filename}")
