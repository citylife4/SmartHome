import warnings

import serial
import serial.tools.list_ports
import time
import logging
from threading import Thread

from enum import Enum

from Arduino.arduino_parser import arduino_parser

# change this
arduino_ports = [
    p.device
    for p in serial.tools.list_ports.comports()
    if 'Arduino' in p.description  # may need tweaking to match new arduinos
]
if not arduino_ports:
    arduino_ports = ['/dev/ttyUSB0']
if len(arduino_ports) > 1:
    warnings.warn('Multiple Arduinos found - using the first')

arduino_ser = serial.Serial(arduino_ports[0],
                            baudrate=9600,
                            parity=serial.PARITY_NONE,
                            stopbits=serial.STOPBITS_ONE,
                            bytesize=serial.EIGHTBITS,
                            timeout=1)


class ArduinoCommands(Enum):
    SET = 0
    GET = 1
    CONFIG = 2


class ArduinoMessage:

    def __init__(self, fromaddr, toaddr, command, gpioaddr, gpiovalue):
        self.fromaddr = fromaddr
        self.toaddr = toaddr
        self.command = command
        self.gpioaddr = gpioaddr
        self.gpiovalue = gpiovalue


class ArduinoThead(Thread):
    def __init__(self):
        super(ArduinoThead, self).__init__()

    def setup(self):
        #pass
        #arduino_ser.write("<0_1_1_13_1>".encode())
        time.sleep(1)
        #arduino_ser.write("<0_1_1_13_0>".encode())
        arduino_ser.write("<0_1_3_4_2>".encode())

    def run(self):
        logging.info("ArduinoThread Function - Starting " + self.name)
        time.sleep(0.1)
        self.setup()
        self.setup()
        last_comunication = 0
        while 1:
            time.sleep(0.01)
            while arduino_ser.in_waiting:  # Or: while ser.inWaiting():
                read_serial = arduino_ser.readline().decode("utf-8")
                arduino_parser(read_serial, last_comunication)
                last_comunication = time.monotonic()
