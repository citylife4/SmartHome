import logging
import socket
import sys

from run import debug
from threading import Thread
from socket_dir import socket_connection, socket_parser


from Arduino.arduino_connection import arduino_ser

class ReceiveThread(Thread):
    def __init__(self, host='', port=4662,name='my_thread'):
        super(ReceiveThread,self).__init__()

        self.connection = None
        self.server = socket.socket(
            socket.AF_INET
            , socket.SOCK_STREAM
        )
        self.server.setsockopt(
            socket.SOL_SOCKET
            , socket.SO_REUSEADDR
            , 1
        )
        self.server.bind((host,port))
        self.server.listen(1)

    def run(self):
        logging.info("ReceiveThread Thread - Starting ")
        #socket_connection.socker_bind_connection()
        while 1:
            #connection can terminate at anytime
            #Try catch??
            connection, addr = self.server.accept()
            rcvd_data = connection.recv(4096).decode("utf-8")
            if rcvd_data:
                socket_parser.rasp_parser(rcvd_data,connection)


class SendThread(Thread):
    def __init__(self):
        super(SendThread,self).__init__()

    def run(self):
        pass
        logging.info("Thread Function - Starting " + self.name)
        socket_connection.send_socket()
        #logging.info("Thread Function - Exiting " + self.name)

class DebugThread(Thread):
    def __init__(self):
        super(DebugThread,self).__init__()

    def run(self):
        logging.info("DebugThread Function - Starting Debug-Mode: "+ str(debug))
        if debug == 1:
            while 1:
                for line in sys.stdin:
                    try:
                        logging.info(line)
                        data_list = list(filter(None, line.strip().split('_')))
                        to_send = "<0_"+data_list[1]
                        if "set" in line:
                            to_send += "_0_"
                        if "get" in line:
                            to_send += "_1_"
                        if "config" in line:
                            to_send += "_2_"
                        if "debug" in line:
                            to_send += "_3_"
                        to_send += data_list[2]+"_"+data_list[3]+ ">"
                        logging.info(to_send)
                        arduino_ser.write( str(to_send).encode() )
                    except:
                        logging.error("Problems: ", sys.exc_info()[0])

