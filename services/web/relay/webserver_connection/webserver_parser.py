import struct
import logging
import threading
from sqlite3 import DatabaseError
import db_interaction as db
from Arduino import arduino_connection

from socket_dir.socket_connection import ip_filename


def send_worker(data):
    arduino_connection.arduino_ser.write("_".join(data).encode())


def h_noop(data):
    print("Not Implemented Received: {}".format(data))


def h_open_porto_door(data):
    t = threading.Thread(target=send_worker, args=(data,))
    t.start()
    return '_'.join(data)


def h_trial(data):
    pass


handlers = {
    "op": h_open_porto_door,
    "tr": h_trial
}


def webserver_parser(data):
    while len(data) >= 2:
        packet_id = data[0:2]
        if packet_id not in handlers:
            data = data[1:]
        else:
            data_list = list(filter(None, data[2:].split('_')))
            data = handlers.get(packet_id, h_noop)(data_list)
