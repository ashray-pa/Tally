from distutils.log import error
from logging import exception
import socket
import threading
import select
from uuid import uuid4
import sys
import time
from datetime import datetime

from connection_handler import Connection
from utils import Utilities
from utils import Acknowldgements
#from chat_app_gui import gui

HOST = "127.0.1.1"
FORMAT = "utf-8"
PORT = 9095
connections = []
clients = []
client_acks = {}  # {client_id1:{dt1:[], dt2:[], .....}, client_id2:{dt1:[], dt2:[], .....}.....}
client_names = []
HEADER = 1024


serverConn = Connection(HOST, PORT)
utils = Utilities()
serverConn.listen_to_clients() 


def handle_request(mess_,conn_r,req_type,writeables):
        if req_type == 'msg':
            msg_sent_time = ""
            client_id = ""

            for line in mess_.split('\r\n'):
                if (line.split(': '))[0] == 'Time':
                    msg_sent_time = line.split(': ')[1]
                elif (line.split(': '))[0] == 'ClientID':
                    client_id = line.split(': ')[1]
                    
            message = mess_.split("\r\n\r\n")[1]
            message=message.split("\r\n")[0]

            sendToAllClients(writeables, message, str(msg_sent_time), client_id)
            client_acks.get(client_id).add_new(msg_sent_time)

            startTimer = threading.Thread(target=checkForAcks, args=(client_id, msg_sent_time,conn_r))
            startTimer.start()

        elif req_type == 'ping':
            msg_sent_time = ""
            client_id = ""

            for line in mess_.split('\r\n'):
                if (line.split(': '))[0] == 'Time':
                    msg_sent_time = line.split(': ')[1]
                elif (line.split(': '))[0] == 'ClientID':
                    client_id = line.split(': ')[1]
            #print("pinged by:", conn_r.getpeername())

            utils.send_ack(socket=conn_r, isMsg=False, id=client_id)

def handle_connections():
    while True:
        if len(connections) > 0:
                readables, writeables, errors = select.select(
                    connections, connections, connections, 1.0)
                try:
                    for conn_r in readables:
                        try:
                            frag=[]
                            data=conn_r.recv(1024).decode(FORMAT)                            
                            while data:
                                l=len(data)
                                p=data[l-3:l] 
                                frag.append(data)
                                if(p=="EOF"):
                                    break
                                
                                data=conn_r.recv(1024).decode(FORMAT)
                            
                            mess_="".join(frag)
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
                                handle_request(mess_,conn_r,req_type,writeables)

                            elif type == 'res':
                                if res_type == 'ack':
                                    #print("message received by:", conn_r.getpeername())
                                    collectAcks(mess_,conn_r)
                                    #print(client_acks[client_id].acks_for_msg__at)

                            if not mess_:
                                print('Disconnected ',conn_r.getpeername())
                                if conn_r in connections:
                                    connections.remove(conn_r)
                                addr = conn_r.getpeername()
                                print(f"{addr} gone")
                                client_names.remove(addr)
                                conn_r.close()
                                
                        except Exception as error:
                       
                            print('Disconnected ',conn_r.getpeername())
                            if conn_r in connections:
                                connections.remove(conn_r)

                            addr = conn_r.getpeername()
                            
                            client_names.remove(addr)
                            conn_r.close()
                    for err in errors:
                        try:
                            print(f"error in connection {err}")
                            connections.remove(err)
                            err.close()
                        except:
                            pass
                except:
                    print('-----Server crashed----')


# def sendToEachClient(socket, message, msg_sent_time, client_id):
#     socket.send(utils.post_req('msg', message, msg_sent_time, client_id).encode())

def checkForAcks(client_id, msg_sent_time,conn_r):
    
    global client_acks
    print("message sent by %s, at %s " %(conn_r.getpeername(), msg_sent_time))
    while True:
        t1=datetime.strptime(msg_sent_time,"%Y-%m-%d %H:%M:%S.%f")
        t2=datetime.now()
        diff=t2-t1
        sec=diff.total_seconds()
        recv_acks=client_acks[client_id].ret_acks(msg_sent_time)

        if(sec>=3 or len(recv_acks)==len(client_names)):
            recv_acks = client_acks[client_id].ret_acks(msg_sent_time)
            print(sec)
            not_recv = []
            for peer in client_names:
                if peer not in recv_acks:
                    not_recv.append(peer)
            if len(not_recv)==0:
                print("message has been sent to all clients")
                utils.send_ack(socket=conn_r, isMsg=True, dt=msg_sent_time, id=client_id)
            else:
                print("Below clients did not receive message:")
                for peer in not_recv:
                    print(peer)
            #print("i was here")
            break

def collectAcks(mess_, conn_r):
    msg_sent_time = ""
    client_id = ""
    for line in mess_.split('\r\n'):
        if (line.split(': '))[0] == 'Time':
            msg_sent_time = line.split(': ')[1]
        elif (line.split(': '))[0] == 'ClientID':
            client_id = line.split(': ')[1]

    client_acks[client_id].add_ack(msg_sent_time, conn_r.getpeername())#here

def sendToAllClients(writeables, message, msg_sent_time, client_id):
    for conn_s in writeables:
        try:
            conn_s.sendall(utils.post_req('msg', message, msg_sent_time, client_id).encode())

        except BrokenPipeError:
            pass


def receive():
    con_thread = threading.Thread(target=handle_connections, args=())
    con_thread.start()
    while True:
        client, addr = serverConn.accept_connection()
        print(f"connected {str(addr)}")
        client.setblocking(0)
        connections.append(client)
        client_names.append(addr)
        client_id = str(uuid4())
        clients.append(client_id)
        acks = Acknowldgements(20)
        client_acks[client_id] = acks

        try:
            client.sendall(utils.get_req("id", client_id).encode())
        except BrokenPipeError:
            print("----- server is down -----")


print("--- server running ---")
print(f"{HOST} is listening")
receive()


#remove disconnected sockets from client peer names
