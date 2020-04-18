import socket
import time
import logging
from sqlite3 import DatabaseError
import db_interaction as db
from Arduino import arduino_connection

connected = False

LOCALHOST = "127.0.0.1"
INTERNAL_PORT = 54897

# This is the address we setup in the Arduino Program
# Slave Address 1
address = 0x04

ip_filename = "/home/jdv/ip_file.txt"


class TCPsocket:

    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(
                socket.AF_INET
                , socket.SOCK_STREAM
            )
            self.sock.setsockopt(
                socket.SOL_SOCKET
                , socket.SO_REUSEADDR
                , 1
            )
        else:
            self.sock = sock
        self.connection = None

    def __del__(self):
        self.sock.close()

    def bind(self, server_address):
        self.sock.bind(server_address)
        self.sock.listen(1)

    def wait_connection(self):
        try:
            self.connection, client_address = self.sock.accept()
            print("ola")
            data = self.connection.recv(1024).decode()
            print(data)
            return data ,client_address
        finally:
            self.connection.close()

    def protocol(self, data):
        return {
            'IP': 'x',
        }.get(data, 'problem')


# create the connection and check if something is getting through
def socker_bind_connection():
    # Bind the socket_connection to the port
    global connected
    connected = False
    server_address = ('', 4662)
    logging.info('waiter_receive_socket - Starting receiver socket_connection up on %s port %s' % server_address)
    slave_socket_connection = TCPsocket()
    slave_socket_connection.bind(server_address)

    # Listen for incoming connections
    while 1:
        data, client_address = slave_socket_connection.wait_connection()
        # condition.acquire()
        logging.info('Received connection from ' + client_address[0])
        # Receive the data in small chunks and retransmit it
        logging.info('Received %s' % data)

        if "IP" in data:
            logging.warning("IP received %s" % client_address[0])
            connected = False
            with open(ip_filename, "w") as ip_file:
                ip_file.write(client_address[0])
            connected = True

        elif "ST" in data:
            logging.warning("Receiving state %s" % data)
            status = data.split("_")[3]
            if status == "True" or status == "False":
                conn = db.insert_state(status)
                if conn is None:
                    raise DatabaseError("Could not get connection")
            else:
                logging.error("Error not implemented - status missing")


def send_socket():
    global connected

    # time.sleep(random.randrange(2, 5))  # Sleeps for some time.
    logging.info('Acquiring lock')
    # condition.acquire()
    logging.info('Waiting for connection %s' % connected)

    # TODO: check how to make with conditions....
    while not connected:
        time.sleep(10)

    # with condition:
    #    condition.wait_for(connected)

    logging.info('Connected %s' % connected)
    # now check if there is someting to send
    while 1:
        if connected:
            sock_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock_send.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # Connect the socket_connection to the port where the server is listening
            ip_file = open("ip_file.txt", "r")
            client_address = ip_file.read()
            ip_file.close()

            server_address = (client_address, 45321)
            logging.info('Connecting Raspberry to %s on %s' % server_address)
            sock_send.connect(server_address)
            try:
                message = "open"
                sock_send.sendall(message.encode('utf-8'))
                data_door = sock_send.recv(1024).decode()
                logging.info('Received %s ' % data_door)
            finally:
                sock_send.close()
        else:
            while not connected:
                time.sleep(10)
                print("Waiting for connection")