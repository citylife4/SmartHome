import socket


class SocketConnection:

    def __init__(self, address, port):
        self.address_client = (address, port)
        self.sock = None

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.connect(self.address_client)

    def close(self):
        self.sock.close()
        self.sock = None

    def send_msg(self, message):
        self.connect()
        self.sock.sendall(message.encode('utf-8'))
        print('Sending %s ' % message)
        receive_data = self.sock.recv(1024).decode()
        print('Received %s ' % receive_data)
        self.close()