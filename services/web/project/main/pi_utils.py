import os


def measure_temp():
    temp = os.popen("vcgencmd measure_temp").readline()
    return temp[5:9]
