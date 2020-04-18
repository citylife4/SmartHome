import struct
import logging
from sqlite3 import DatabaseError
import db_interaction as db

from socket_dir.socket_connection import ip_filename


def h_noop(data, connection):
    logging.error("Not Implemented Received: {}".format(data))


def h_update_ip(data, connection):
    logging.info("h_update_ip: {}".format(data))
    ip_address = data.pop(0)
    with open(ip_filename, "w") as ip_file:
        ip_file.write(ip_address)
    connection.sendall("porto_done".encode('utf-8'))
    return '_'.join(data)


def h_update_status(data, connection):
    logging.info("h_update_status: {}".format(data))
    status = data.pop(0)
    conn = db.insert_state(status)
    if conn is None:
        raise DatabaseError("Could not get connection")
    return '_'.join(data)


def h_check_connection(data, connection):
    logging.info("h_check_connection: {}".format(data))
    connection.sendall("porto_done".encode('utf-8'))
    logging.info("h_check_connection: sent")
    return '_'.join(data)


handlers = {
    "ip": h_update_ip,
    "st": h_update_status,
    "ch": h_check_connection
}


def rasp_parser(data, connection):
    while len(data) >= 2:
        packet_id = data[0:2]
        if packet_id not in handlers:
            data = data[1:]
        else:
            data_list = list(filter(None, data[2:].split('_')))
            data = handlers.get(packet_id, h_noop)(data_list, connection)
