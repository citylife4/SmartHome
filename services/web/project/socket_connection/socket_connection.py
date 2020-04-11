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


def send_socket(message):
    # global connected

    # time.sleep(random.randrange(2, 5))  # Sleeps for some time.
    # logging.info('Aquiring lock')
    # condition.acquire()
    # logging.info('Waiting for connection %s' % connected)

    # TODO: check how to make with conditions....
    # while not connected:
    #    time.sleep(10)

    # with condition:
    #    condition.wait_for(connected)

    # logging.info('Connected %s' % connected)
    # now check if there is someting to send
    # if connected:

    sock_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_send.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Connect the socket_connection to the port where the server is listening
    # ip_file = open("/home/jdv/ip_file.txt", "r+")
    # client_address = ip_file.read()
    # ip_file.close()

    # TODO Change this
    server_address = ("dvpalacoulo.dynip.sapo.pt", 45321)
    print('Connecting Raspberry to %s on %s' % server_address)
    sock_send.connect(server_address)
    receive_data = None

    try:
        sock_send.sendall(message.encode('utf-8'))

        amount_received = 0
        amount_expected = len(message)

        while amount_received < amount_expected:
            receive_data = sock_send.recv(16).decode()
            amount_received += len(receive_data)
        print("received {!r}".format(receive_data))

    finally:
        sock_send.close()
        return receive_data
