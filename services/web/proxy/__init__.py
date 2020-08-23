
from .relay_proxy import Relay2Proxy
from .relay_proxy import Proxy2Relay
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

class Proxy(Thread):

    def __init__(self, from_host, to_host, port=54897):
        super(Proxy, self).__init__()
        self.from_host = from_host
        self.to_host = to_host ##TODO Remove
        self.port = port

        self.connected_ports = []
        self.running = False

    def run(self):
        r2pdict = {}
        p2rdict = {}
        while True:
            print("[Proxy({})] setting up".format(self.port))
            r2p = Relay2Proxy(self.from_host, self.port)  # waiting for a client
            # self.r2r = Relay2Rasp(self.to_host, self.port)
            print("[Proxy({})] connection established".format(self.port))
            # self.r2p.rasp = self.r2p.rasp
            # self.r2r.web = self.r2p.web
            if not r2p.invalid:

                #TODO: Addr can change
                p2r = Proxy2Relay(r2p.addr[0],r2p.name, 45321)
                if r2p.addr[0] not in p2rdict.keys():
                    print("[Proxy({})] Creating new Proxy2Relay".format(self.port))
                else:
                    print("[Proxy[{}]] Terminating Proxy2Relay[{}]".format(self.port,r2p.addr[0]))
                    print("[Proxy[{}]] {}".format(self.port,p2rdict))
                    p2rdict[r2p.addr[0]].close_connection = True
                    p2rdict[r2p.addr[0]].join()
                    p2rdict.pop(r2p.addr[0])
                    #TODO Terminate
                
                
                #Delete last thread if available
                if r2p.host_port in r2pdict.keys():
                    print("[Proxy[{}]] Terminating Relay2Proxy[{}]".format(self.port,r2p.host_port))
                    print("[Proxy[{}]] {}".format(self.port,r2pdict))
                    r2pdict[r2p.host_port].close_connection = True
                    r2pdict[r2p.host_port].join()
                    r2pdict.pop(r2p.host_port)
                    
                p2rdict[r2p.addr[0]] = p2r
                r2pdict[r2p.host_port] = r2p
                print("[Proxy({})] connection Starting".format(self.port))
                #create p2r firts
                r2p.start()
                p2r.start()
                # self.r2r.start()
