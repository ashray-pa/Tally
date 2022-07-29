from distutils.log import error
from logging import exception
import socket
import threading
import select
import sys
import time

from connection_handler import Connection
from utils import Utilities

HOST = "127.0.1.1"
FORMAT = "utf-8"
PORT = 9095
connections = []
HEADER = 1024


serverConn = Connection(HOST, PORT)
utils = Utilities()
serverConn.listen_to_clients()

def handle_connections():
    while True:
        if len(connections) > 0:
                readables, writeables, errors = select.select(
                    connections, connections, connections, 1.0)

                for conn_r in readables:
                    try:
                        mess_ = conn_r.recv(HEADER).decode(FORMAT)
                        type = ''
                        req_type = ''
                        res_type = ''

                        for line in mess_.split('\r\n'):
                            if(line.split(': ')[0] == 'Req-Type' or line.split(': ')[0] == 'Res-Type'):
                                if(line.split(': ')[0] == 'Req-Type'):
                                    type = 'req'
                                    req_type = line.split(': ')[1]
                                else:
                                    type = 'res'
                                    res_type = line.split(': ')[1]

                        if type == 'req':
                            if req_type == 'msg':
                                message = mess_.split("\r\n\r\n")[1]
                                utils.send_ack(socket=conn_r, isMsg=True)
                                writeToAll = threading.Thread(target=sendToAllClients, args=(writeables, message))
                                writeToAll.start()

                            elif req_type == 'ping':
                                #print("pinged by:", conn_r.getpeername())
                                utils.send_ack(socket=conn_r, isMsg=False)

                        elif type == 'res':
                            if res_type == 'ack':
                                print("message received by:", conn_r.getpeername())

                        if not mess_:
                            print('Disconnected',conn_r)
                            if conn_r in connections:
                                connections.remove(conn_r)
                            conn_r.close()
                            
                    except Exception as error:
                        print(error)
                        print("--- error ---")
                for err in errors:
                    try:
                        print(f"error in connection {err}")
                        connections.remove(err)
                        err.close()
                    except:
                        pass

def receive():
    con_thread = threading.Thread(target=handle_connections, args=())
    con_thread.start()
    while True:
        client, addr = serverConn.accept_connection()
        print(f"connected {str(addr)}")
        client.setblocking(0)
        connections.append(client)

def sendToEachClient(socket, message):
    socket.send(utils.post_req('msg', message).encode())

    # try:
    #     socket.setblocking(1)
    #     socket.settimeout(5)
    #     socket.recv(HEADER).decode(FORMAT)
    #     socket.settimeout(0)
    #     socket.setblocking(0)
    #     print("(below)message received by:", socket.getpeername())
    # except Exception as e:
    #     print(e)

def sendToAllClients(writeables, message):
    for conn_s in writeables:
        try:
            #sendToEachClient(conn_s, message)
            writeToEach = threading.Thread(target=sendToEachClient, args=(conn_s, message))
            writeToEach.start()

        except BrokenPipeError:
            pass

print("--- server running ---")
print(f"{HOST} is listening")
receive()
