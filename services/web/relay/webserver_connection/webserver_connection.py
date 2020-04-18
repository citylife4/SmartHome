import socket
from threading import Thread
from time import sleep
import logging

from Arduino import arduino_connection
from socket_dir.socket_connection import LOCALHOST, INTERNAL_PORT
from webserver_connection.webserver_parser import webserver_parser


class WebserverConnection(Thread):
    def __init__(self):
        super(WebserverConnection,self).__init__()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((LOCALHOST, INTERNAL_PORT))
        logging.info('Waiting for internal Application')

    def run(self):
        pass
        logging.info("WebserverConnection Function - Starting ")

        try:
            while True:
                self.server.listen(1)
                client_connection, client_address = self.server.accept()
                data = client_connection.recv(1024).decode()
                logging.info("WebserverConnection - Receiving: %s", data)
                webserver_parser(data)
                client_connection.send("received".encode())

        finally:
            logging.info("WebserverConnection - Receiving - Closing")
            self.server.close()
            # change this
