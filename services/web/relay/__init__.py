
from .relay_proxy import Relay2Web
from .relay_proxy import Web2Relay
from threading import Thread
import logging

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
