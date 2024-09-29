import socket
import struct
import threading

# Fungsi untuk menerima pesan dari grup multicast
def receive_messages(sock):
    while True:
        try:
            data, address = sock.recvfrom(1024)
            print(f"Message from {address}: {data.decode()}")
        except Exception as e:
            print(f"Error receiving message: {e}")
            break

def main():
    multicast_group = '224.0.0.1'
    port = 5007

    # Membuat socket untuk bergabung dengan grup multicast
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', port))

    # Bergabung dengan grup multicast
    group = socket.inet_aton(multicast_group)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    # Membuat thread untuk menerima pesan
    receive_thread = threading.Thread(target=receive_messages, args=(sock,))
    receive_thread.start()

    # Mengirim pesan ke grup multicast
    while True:
        message = input("You: ")
        sock.sendto(message.encode(), (multicast_group, port))

if __name__ == "__main__":
    main()
