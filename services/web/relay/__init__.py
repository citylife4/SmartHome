import socket
from threading import Thread

# from relay.Thread_package.thead_classes import *
# from relay.Arduino import arduino_connection
# from relay.webRasp_connection.webRasp_connection import WebRaspConnection


class Web2Relay(Thread):

    def __init__(self, host, port):
        super(Web2Relay, self).__init__()
        self.rasps = {}  # can contain many
        self.port = port
        self.host = host
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        print("Web2Relay[{}] -> Starting".format(self.port))
        sock.listen(1)
        self.sock = sock

    def run(self):
        while True:
            # waiting for a connection
            self.Web, addr = self.sock.accept()
            data = self.Web.recv(4096)
            if data:
                data = data.decode().split('_', 1)
                print("[{}] -> {}".format(self.port, data))
                try:
                    print(self.rasps[data[0]])
                    # parser.parse(data, self.port, 'client')
                    # if len(parser.Rasp_QUEUE)>0:
                    #    pkt = parser.Rasp_QUEUE.pop()
                    #    #print "got queue Rasp: {}".format(pkt.encode('hex'))
                    #    self.Rasp.sendall(pkt)
                except Exception as e:
                    print('client[{}]'.format(self.port), e)
                # forward to Rasp
                # self.Rasp.sendall(data)

#
# py_web   <--->    db
#             |
#            py_relay
#     |                 |
#    py_porto           py_palacoulo
#     |
#     porta / sensor


class Relay(Thread):

    def __init__(self, from_host, to_host, port):
        super(Relay, self).__init__()
        self.from_host = from_host
        self.to_host = to_host
        self.port = port
        self.running = False

    def run(self):
        print("[Relay({})] setting up".format(self.port))
        self.w2r = Web2Relay(self.from_host, self.port)  # waiting for a client
        # self.r2r = Relay2Rasp(self.to_host, self.port)
        print("[Relay({})] connection established".format(self.port))
        # self.w2r.rasp = self.w2r.rasp
        # self.r2r.web = self.w2r.web
        self.running = True

        self.w2r.start()
        print("[Relay({})] connection established".format(self.port))
        self.w2r.rasps.update({"palacoulo": "ppcoulo"})
        self.w2r.rasps.update({"porto": "ppporto"})
        # self.r2r.start()
