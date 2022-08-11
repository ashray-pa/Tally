import socket
import time
# from ping3 import ping
from utils import Utilities

FORMAT = "utf-8"
PING_CODE = "pingCheck"
utils = Utilities()

class Connection:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect_to_server(self):
        try:
            self.sock.connect((self.host, self.port))
        except Exception as e:
            print("server is not up")
            exit(0)
        self.running = False
        self.server_status = "up"
        self.server_down_cnt = 1

    def listen_to_clients(self):
        self.sock.bind((self.host, self.port))
        self.sock.listen()

    def accept_connection(self):
        return self.sock.accept()

    def server_down_close(self):
        print("--- closing client ---\n3")
        time.sleep(1)
        print("2")
        time.sleep(1)
        print("1")
        time.sleep(1)
        self.running = False
    
    def sendMessage(self, msg, dt, id):
        self.sock.sendall(utils.post_req("msg", msg, dt, id).encode())

    def recvFun(self):
        frag=[]
        mess_=self.sock.recv(1024).decode(FORMAT)
        while mess_:
            frag.append(mess_)
            l=len(mess_)
            p=mess_[l-3:l]
            if p=="EOF":
                break
            mess_=self.sock.recv(1024).decode(FORMAT)
           
        return "".join(frag)

    def ping_(self):
        try:
            self.sock.sendall(utils.get_req("ping", PING_CODE).encode())
            time.sleep(5)
        except Exception as e:
            self.server_status = "down"
            self.server_down_close()

    def recvId(self):
        return self.sock.recv(1024).decode(FORMAT)

    def closeConn(self):
        self.sock.close()

    # def ping(self):
    #     res = ping(self.host)
    #     if res==False:
    #         self.server_status = "down"
    #         self.server_down_close()
    #     else:
    #         print("pinged")
    #         time.sleep(5)
    #         ping()

#to test 1
