from datetime import datetime
from queue import PriorityQueue

class Utilities:  
    def post_req(self, req_type, data, dt, id):
        return 'POST HTTP/1.1 \r\nContent-Type: text/html\r\nContent-Length: %d\r\nReq-Type: %s\r\nTime: %s\r\nClientID: %s\r\n\r\n%s' %(len(data), req_type, dt, id, data)

    def get_req(self, req_type, data):
        return 'GET HTTP/1.1 \r\nContent-Type: text/html\r\nContent-Length: %d\r\nReq-Type: %s\r\n\r\n%s' %(len(data), req_type, data)

    def post_res(self, res_type, data, dt, id):
        return 'HTTP/1.1 \r\nContent-Type: text/html\r\nContent-Length: %d\r\nRes-Type: %s\r\nTime: %s\r\nClientID: %s\r\n\r\n%s' %(len(data), res_type, dt, id, data)

    def send_ack(self, socket, isMsg, id, dt=None):
        if isMsg:
            socket.send('HTTP/1.1 \r\nContent-Type: text/html\r\nRes-Type: ack\r\nTime: {dt}\r\nClientID: {id}'.format(dt=dt, id=id).encode())
            #print('HTTP/1.1 \r\nContent-Type: text/html\r\nRes-Type: ack\r\nTime:%s'.encode() %dt)
        else:
            socket.send('HTTP/1.1 \r\nContent-Type: text/html\r\nRes-Type: ackp'.encode())


class Acknowldgements:
    def __init__(self, max_size):
        self.acks_for_msg__at = {}
        self.max_size=max_size

    def add_new(self, datetime):
        self.acks_for_msg__at[datetime] = []
        print(len(self.acks_for_msg__at))
        if(len(self.acks_for_msg__at)>self.max_size):
        	keys = list(self.acks_for_msg__at.keys())
        	time = keys[0]
        	del self.acks_for_msg__at[time]

    def ret_acks(self, datetime):
        return self.acks_for_msg__at[datetime]

    def add_ack(self, datetime, peerName):
        self.acks_for_msg__at[datetime].append(peerName)
