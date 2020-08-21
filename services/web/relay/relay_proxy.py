
import socket
import time
from threading import Thread
import logging
from .relay_parser import parser

# from relay.Thread_package.thead_classes import *
# from relay.Arduino import arduino_connection
# from relay.webRasp_connection.webRasp_connection import WebRaspConnection
from Crypto.Cipher import AES
from Crypto.Util import Counter

key = b'Jimmy ffffffffff'
IV = b'1234567891234567'
WEB2RELAY_MAX_TIMOUT = 5

valid_ports     = list(range(4000,4050))
known_hosts     = {} #TODO: Save in DB
connected_ports = []
connected_addr  = []

def do_encrypt(message):
    iv_int = int.from_bytes(IV, byteorder='big')

    new_counter = Counter.new(128, initial_value=iv_int)
    cipher = AES.new(key, AES.MODE_CTR, counter=new_counter)
    return cipher.encrypt(message)

def do_decrypt(message):
    iv_int = int.from_bytes(IV, byteorder='big')
    new_counter = Counter.new(128, initial_value=iv_int)
    cipher = AES.new(key, AES.MODE_CTR, counter=new_counter)
    return cipher.decrypt(message)


class Web2Relay(Thread):

    def __init__(self, host, name, port):
        super(Web2Relay, self).__init__()
        self.rasps = {}  # can contain many
        self.port = port
        self.parent_name = name
        self.host = host
        self.first_connection = True
        self.close_connection = False
        self.invalid = False
        print("[Web2Relay[{}] {}] Starting".format(self.host,self.parent_name))

    def check_connection(self, sender_sock, timout=0):
        if self.close_connection or timout == WEB2RELAY_MAX_TIMOUT:
            print("[Web2Relay[{}] {}] Terminating".format(self.host,self.parent_name))
            sender_sock.close()
            return 1
        return 0

    def run(self):
        #General While
        while True:

            message = "ch_on"
            #While for the timout
            timout = 1
            while True:
                sender_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sender_sock.settimeout(9)
                if self.check_connection(sender_sock, timout): return 0
                try:
                    print("[Web2Relay[{}] {}] Connecting".format(self.host,self.parent_name))
                    sender_sock.connect( (self.host,self.port) )
                    break
                except socket.timeout:
                    timout = WEB2RELAY_MAX_TIMOUT
                except socket.error as e:
                    logging.error("[Web2Relay[{}] {}]  Cant connect at the time {}".format(self.host, self.parent_name,str(e)))
                    time.sleep(10)
                    timout += 1
                    continue
            print("[Web2Relay[{}] {}] Connected".format(self.host,self.parent_name))

            #While for the Conection
            while True:
                if self.check_connection(sender_sock): return 0
                time.sleep(1)
                #if 
                print("[Web2Relay[{}] {}] Sending {}".format(self.host,self.parent_name,message))
                try:
                    # For now do nothing
                    #sender_sock.sendall(do_encrypt(str(message)))
                    time.sleep(1)
                    #received_data = do_decrypt(sender_sock.recv(16)).decode()
                except socket.timeout:
                    if self.check_connection(sender_sock): return 0
                except ConnectionResetError as e:
                    print("[Web2Relay[{}] {}] {}".format(self.host, self.parent_name,str(e)))
                    continue
                except Exception as e:
                    print("[Web2Relay[{}] {}] {}".format(self.host, self.parent_name,str(e)))
                    continue
                
                # For now no back com trough this socket
                #try:
                #    print("[Web2Relay[{}] {}] Received: {}".format(self.host,self.parent_name,received_data))
                #except Exception as e:
                #    sender_sock.close()
                #    # connection error event here, maybe reconnect
                #    print( '[Web2Relay[{}] {}] connection error: {}'.format(self.host,self.parent_name,str(e)))
                #    break

        


class Relay2Web(Thread):

    def __init__(self, host, port):
        super(Relay2Web, self).__init__()
        self.rasps = {}  # can contain many
        self.connection_port = port
        self.host = host
        self.first_connection = True
        self.close_connection = False
        self.invalid = False

        self.host_port = self.appoint_port(port)

        if self.host_port == 0:
            print("[Relay2Web[{}]] Terminating".format(self.host_port))
            self.invalid = True



    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.host_port))
        sock.settimeout(1)
        sock.listen(1)
        while True:
            print("[Relay2Web[{}] {}] Waiting connection".format(self.name,self.host_port))
            while True:
                try:
                    relay, addr = sock.accept()
                    break
                except socket.timeout:
                    #print("timout")
                    if self.close_connection == True:
                        print("[Relay2Web[{}] {}] Terminating".format(self.name,self.host_port))
                        sock.close()
                        return 0
            print("[Relay2Web[{}] {}] Connection Extablished".format(self.name,self.host_port))
            receveid_data = relay.recv(4096)
            data = do_decrypt(receveid_data)
            print("[Relay2Web[{}] {}] Received: {}".format(self.name,self.host_port, data))
            if data:
                try:
                    data = data.decode()
                    parser(data)
                    print("[Relay2Web[{}] {}] -> {}".format(self.host_port,self.name, data))
                    relay.sendall(do_encrypt("Correct"))

                except Exception as e:
                    print('[Relay2Web[{}] {}] - {}'.format(self.host_port,self.name, str(e)))
                    print('[Relay2Web[{}] {}] - {}'.format(self.host_port,self.name, str(receveid_data)))
                # forward to Rasp
                # self.Rasp.sendall(data)

    #Do 
    def appoint_port(self, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, port))
        print("[Relay2Web[{}]] -> Starting".format(port))

        sock.listen(1)

        #TODO: Check if needed
        while True:
            try:
                relay_socket, self.addr = sock.accept()
                original_msg = relay_socket.recv(4096)
                relay_socket_received_data = do_decrypt(original_msg)
                if relay_socket_received_data:
                    relay_first_data = relay_socket_received_data.decode().split('_')
            except Exception as e:
                print("[Relay2Web[{}]] Problems on accepting {} ({})".format(port, relay_socket_received_data, original_msg))
                print("[Relay2Web[{}]] {}".format(port,str(e)))
                sock.close()
                return 0

            print("[Relay2Web[{}]] -> ".format(port), relay_first_data)
            try:
                if relay_first_data[0] == 'connect':
                    host_port = known_hosts[relay_first_data[1]]
                    print("[Relay2Web[{}]] Existing relay: {}:{}".format(host_port,relay_first_data[1],host_port) )
                else:
                    print("[Relay2Web[{}]] wrong Info")
                    sock.close()
                    return 0
            except Exception as e:
                host_port = valid_ports.pop(0)
                known_hosts[relay_first_data[1]] = host_port
                print("[Relay2Web[{}]] New relay: {}:{}".format(host_port,relay_first_data[1],host_port) )
            
            print("[Relay2Web[{}]] ".format(host_port) ,host_port)
            print("[Relay2Web[{}]] ".format(host_port) ,known_hosts)


            try:
                relay_socket.sendall(do_encrypt("server_"+str(host_port)))
            except Exception as e:
                known_hosts.pop(relay_first_data[1], None)
                valid_ports.insert(0,host_port)
                print("[Relay2Web[{}]] Problems on sending".format(host_port))
                print("[Relay2Web[{}]] {}".format(host_port,str(e)))
                sock.close()
                return 0
            self.name="_".join(relay_first_data)
            sock.close()
            return host_port

