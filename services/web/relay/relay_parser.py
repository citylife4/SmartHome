
SERVER_QUEUE = []
CLIENT_QUEUE = []


def h_noop(data):
    print("[Connection Parser] Not Implemented Received: {}".format(data))
 
def h_relay_gpio(data):
    print("[Connection Parser] Received h_relay_gpio: : {}".format(data))
    return '_'.join(data)

handlers = {
    "gp": h_relay_gpio,
}


def parser(data):
    while len(data) >= 2:
        packet_id = data[0:2]
        if packet_id not in handlers:
            print(data)
            data = data[1:]
        else:
            data_list = list(filter(None, data[2:].split('_')))
            data = handlers.get(packet_id, h_noop)(data_list)
