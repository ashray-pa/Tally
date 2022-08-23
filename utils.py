from datetime import datetime
from queue import PriorityQueue

class Utilities:  
    def post_req(self, req_type, data, dt, id):
        return 'POST HTTP/1.1 \r\nContent-Type: text/html\r\nContent-Length: %d\r\nReq-Type: %s\r\nTime: %s\r\nClientID: %s\r\n\r\n%s\r\nEOF'%(len(data),
         req_type, dt, id, data)

    def get_req(self, req_type, data):
        return 'GET HTTP/1.1 \r\nContent-Type: text/html\r\nContent-Length: %d\r\nReq-Type: %s\r\n\r\n%s\r\nEOF' %(len(data), req_type, data)

    def send_ack(self, socket, isMsg, id, dt=None):
        if isMsg:
            socket.sendall('HTTP/1.1 \r\nContent-Type: text/html\r\nRes-Type: ack\r\nTime: {dt}\r\nClientID: {id}\r\nEOF'.format(dt=dt, id=id)
            .encode())
            #print('HTTP/1.1 \r\nContent-Type: text/html\r\nRes-Type: ack\r\nTime:%s'.encode() %dt)
        else:
            socket.sendall('HTTP/1.1 \r\nContent-Type: text/html\r\nRes-Type: ackp\r\nEOF'.encode())


class Acknowledgements:
    def __init__(self, max_size):
        self.acks_for_msg__at = {}    # dictionary of acknowledgements for each message 
        self.max_size=max_size        # {dt_1:[], dt_2:[], dt_3:[], ....dt_max_size:[]}

    def add_new(self, datetime):                      # add a dictionary element for new message sent by the client at 'datetime'
        self.acks_for_msg__at[datetime] = []          # initilize with empty list of responded clients
        if(len(self.acks_for_msg__at)>self.max_size): # if dictionary has more than max_size elements, delete the oldest message's response list
            keys = list(self.acks_for_msg__at.keys())
            time = keys[0]
            del self.acks_for_msg__at[time]

    def ret_acks(self, datetime):
        return self.acks_for_msg__at[datetime]        # return the list of clients who have responded for the message sent at 'datetime' 

    def add_ack(self, datetime, peerName):            # add the client who has responded for the message sent at 'datetime' into the response list 
        self.acks_for_msg__at[datetime].append(peerName)
