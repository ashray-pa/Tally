import time
from ping3 import ping
from connection_handler import Connection

HOST = "127.0.1.1"
PORT = 9095

client = Connection(HOST, PORT)
client.connect_to_server()

def ping1():
        res = ping(HOST)

        if res==False:
            print("pinged")
        else: 
            time.sleep(5)
            ping1()

ping1()