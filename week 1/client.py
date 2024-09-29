import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_IP = '180.23.3.6'
server_PORT = 5000

client_socket.connect((server_IP, server_PORT))
print('Client connected to {}:{}'.format(server_IP, server_PORT))

massage = input('Enter message: ')
client_socket.send(massage.encode())

response = client_socket.recv(1024).decode()
print("server response: ",response)

client_socket.close()