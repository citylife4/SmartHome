import socket
import time
from threading import Thread
import logging

# from relay.Thread_package.thead_classes import *
# from relay.Arduino import arduino_connection
# from relay.webRasp_connection.webRasp_connection import WebRaspConnection
from Crypto.Cipher import AES
from Crypto.Util import Counter

key = b'Jimmy ffffffffff'
IV = b'1234567891234567'

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

    def check_connection(self,sender_sock):
        if self.close_connection:
            print("[Web2Relay[{}] {}] Terminating".format(self.host,self.parent_name))
            sender_sock.close()
            return 1
        return 0

    def run(self):
        #General While
        while True:

            message = "dt_123"
            #While for the timout
            while True:
                sender_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sender_sock.settimeout(9)
                try:
                    print("[Web2Relay[{}] {}] Connecting".format(self.host,self.parent_name))
                    sender_sock.connect( (self.host,self.port) )
                    break
                except socket.timeout:
                    if self.check_connection(sender_sock): return 0
                except socket.error as e:
                    logging.error("[ClientThread] Cant connect at the time {}".format(e))
                    time.sleep(10)
                    continue
            print("[Web2Relay[{}] {}] Connected".format(self.host,self.parent_name))

            #While for the Conection
            while True:
                if self.check_connection(sender_sock): return 0
                time.sleep(1)
                print("[Web2Relay[{}] {}] Sending {}".format(self.host,self.parent_name,message))
                try:
                    sender_sock.sendall(do_encrypt(str(message)))
                    time.sleep(1)
                    received_data = do_decrypt(sender_sock.recv(16)).decode()
                except socket.timeout:
                    if self.check_connection(sender_sock): return 0
                except ConnectionResetError as e:
                    print("[Web2Relay[{}] {}] ".format(self.host, self.parent_name,str(e)))
                    break
                except Exception as e:
                    print("[Web2Relay[{}] {}] {}".format(self.host, self.parent_name,str(e)))
                    break

                if received_data:
                    print("[Web2Relay[{}] {}] Received: {}".format(self.host,self.parent_name,received_data))
                if not received_data:
                    sender_sock.close()
                    # connection error event here, maybe reconnect
                    print( '[Web2Relay[{}] {}] connection error')
                    break

        


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
            print("[Relay2Web[{}]] Deliting".format(self.host_port))
            self.invalid = True



    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.host_port))
        sock.settimeout(1)
        sock.listen(1)
        while True:


            print("[Relay2Web[{}] {}] accepting".format(self.name,self.host_port))
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
            print("[Relay2Web[{}] {}] broke".format(self.name,self.host_port))
            receveid_data = relay.recv(4096)
            data = do_decrypt(receveid_data)
            if data:
                try:
                    data = data.decode().split('_')
                    print("[Relay2Web[{}] {}] -> {}".format(self.host_port, data))
                    relay.sendall(do_encrypt(data[0]))

                except Exception as e:
                    print('[Relay2Web[{}] {}] - {}'.format(self.host_port, str(e)))
                    print('[Relay2Web[{}] {}] - {}'.format(self.host_port, str(receveid_data)))
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
                if relay_first_data[0] == 'ch':
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




#
# py_web   <--->    db
#             |
#            py_relay
#     |                 |
#    py_porto           py_palacoulo
#     |
#     porta / sensor


class Relay(Thread):

    def __init__(self, from_host, to_host, port=54897):
        super(Relay, self).__init__()
        self.from_host = from_host
        self.to_host = to_host ##TODO Remove
        self.port = port

        self.connected_ports = []
        self.running = False

    def run(self):
        r2wdict = {}
        w2rdict = {}
        while True:
            print("[Relay({})] setting up".format(self.port))
            r2w = Relay2Web(self.from_host, self.port)  # waiting for a client
            # self.r2r = Relay2Rasp(self.to_host, self.port)
            print("[Relay({})] connection established".format(self.port))
            # self.r2w.rasp = self.r2w.rasp
            # self.r2r.web = self.r2w.web
            if not r2w.invalid:

                #TODO: Addr can change
                w2r = Web2Relay(r2w.addr[0],r2w.name, 45321)
                if r2w.addr[0] not in w2rdict.keys():
                    print("[Relay({})] Creating new Web2Relay".format(self.port))
                else:
                    print("[Relay[{}]] Terminating Web2Relay[{}]".format(self.port,r2w.addr[0]))
                    print("[Relay[{}]] {}".format(self.port,w2rdict))
                    w2rdict[r2w.addr[0]].close_connection = True
                    w2rdict[r2w.addr[0]].join()
                    w2rdict.pop(r2w.addr[0])
                    #TODO Terminate
                
                
                #Delete last thread if available
                if r2w.host_port in r2wdict.keys():
                    print("[Relay[{}]] Terminating Relay2Web[{}]".format(self.port,r2w.host_port))
                    print("[Relay[{}]] {}".format(self.port,r2wdict))
                    r2wdict[r2w.host_port].close_connection = True
                    r2wdict[r2w.host_port].join()
                    r2wdict.pop(r2w.host_port)
                    
                w2rdict[r2w.addr[0]] = w2r
                r2wdict[r2w.host_port] = r2w
                print("[Relay({})] connection Starting".format(self.port))
                #create w2r firts
                r2w.start()
                w2r.start()
                # self.r2r.start()
