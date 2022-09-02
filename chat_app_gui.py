from datetime import datetime
from http import server
import threading
import tkinter
from tkinter import simpledialog
import tkinter.scrolledtext
from connection_handler import Connection
from utils import Utilities
from tkinter import messagebox
###############################################

HOST = "127.0.1.1"
PORT = 9095
utils = Utilities()



class ChatApp:
    def __init__(self):
        #self.conn = Connection(HOST, PORT)
        #self.conn.connect_to_server()
       
        self.reconnection()
        if(self.conn.running):
            msg = tkinter.Tk()
            msg.withdraw()
            self.name = simpledialog.askstring(
                "Name", "Enter your name", parent=msg)
            if not self.name:
                self.conn.server_down_close()

    def reconnection(self):
        
        self.conn=Connection(HOST,PORT)
        self.conn.connect_to_server()
        if self.conn.running:
            self.client_id = self.conn.recvId().split('\r\n\r\n')[1]
            self.client_id=self.client_id.split("\r\n")[0]
            print("the new client id is ",self.client_id)
            recv_thread = threading.Thread(target=self.read_)
            down_thread = threading.Thread(target=self.ping_)
        # gui_thread.daemon = True
            recv_thread.daemon = True
            down_thread.daemon = True
            # gui_thread.start()
            recv_thread.start()
            down_thread.start()
        else:
            self.conn.server_down_close()

             
        
          

        #print("i have no clue")

    def gui_(self):
        self.window = tkinter.Tk(className=self.name)
        self.window.configure(bg="black")

        self.chat_label = tkinter.Label(
            self.window,bg="black", text="Chat:", fg="white")
        self.chat_label.config(font=("Arial", 12, "bold"))
        self.chat_label.pack(padx=5, pady=5)

        self.text_area = tkinter.scrolledtext.ScrolledText(
            self.window, bg="#2a282b", fg="white", font=("Arial", 12, "bold"))
        self.text_area.pack(padx=20, pady=5)
        self.text_area.config(state="disabled")

        self.msg_label = tkinter.Label(
            self.window, text="message:", bg="black", fg="white")
        self.msg_label.config(font=("Arial", 12, "bold"))
        self.msg_label.pack(padx=20, pady=5)

        self.msg_input = tkinter.Text(
            self.window, height=2, bg="#2a282b", fg="white",insertbackground='white',
            font=("Arial", 12, "bold"))
        self.msg_input.pack(padx=20, pady=5)

        self.send_btn = tkinter.Button(
            self.window, text="send", command=self.write_)
        self.send_btn.config(font=("Arial", 12))
        self.send_btn.pack(padx=20, pady=5)

        self.notify = tkinter.Label(
            self.window, text="message sent", bg="black", fg="green")
        self.notify.config(font=("Arial", 12))

        self.gui_done = True
        self.window.protocol("WM_DELETE_WINDOW", self.stop_)
        self.window.mainloop()


    def write_(self):
        message = f"{self.name}: {self.msg_input.get('1.0', 'end')}"
        try:
            if self.conn.running:
                self.conn.sendMessage(message, str(datetime.now()), self.client_id)
        except BrokenPipeError:
            print("----- server is down -----")
            
            self.server_down_cnt = self.server_down_cnt - 1
            if self.server_down_cnt <= 0:
                self.conn.server_down_close()
                self.window.destroy()        
        self.msg_input.delete('1.0', 'end')


    def read_(self):
        while self.conn.running:
            try:
                res_type = ""
                req_type = ""
                mess_ = self.conn.recvFun()

                if mess_.startswith("HTTP"):
                    for line in mess_.split('\r\n'):
                        if(line.split(': ')[0] == 'Res-Type'):
                            res_type = line.split(': ')[1]
                    if True:
                        if res_type == 'ack':
                            print('HTTP/1.1 200 OK message sent')
                            self.notify.place(relx=1.0, rely=0.0, anchor = 'ne')
                            self.notify.after(2000, lambda: self.notify.place_forget())

                        elif res_type == 'ackp':
                            pass

                else:
                    for line in mess_.split('\r\n'):
                        if(line.split(': ')[0] == 'Req-Type'):
                            req_type = line.split(': ')[1]

                    if req_type=='msg':
                        msg_sent_time = None
                        client_id = None
                        for line in mess_.split('\r\n'):
                            if (line.split(': '))[0] == 'Time':
                                msg_sent_time = line.split(': ')[1]
                            elif (line.split(': '))[0] == 'ClientID':
                                client_id = line.split(': ')[1]

                        message = mess_.split("\r\n\r\n")[1]
                        message=message.split("\r\n")[0]
                        self.text_area.config(state="normal")
                        self.text_area.insert("end", message)
                        self.text_area.yview("end")
                        self.text_area.config(state="disabled")
                        utils.send_ack(socket=self.conn.sock, isMsg=True, dt=msg_sent_time, id=client_id)

            except ConnectionAbortedError:
                print("here 163")
                break
            except Exception as e:
                print("please handle this error",e)
                
                exit(0)
                #self.conn.closeConn()
                


    def stop_(self):
        res = messagebox.askokcancel('Ok Close', 'Are You sure?')
        if res:
            self.conn.running = False
            self.window.destroy()
            self.conn.closeConn()
            exit(0)


    def ping_(self):
        while self.conn.running:
            self.conn.ping_()
            try:
                if self.conn.server_status == "down":
                    
                    self.conn.closeConn() 
                    self.reconnection()     
                    
                    if(self.conn.running==False):     
                        self.window.destroy() 
                        exit(0)        
            except:
                print('---client closed---')
                exit(0)

            

gui = ChatApp()
try:
    gui.gui_()
except:
    print('GUI terminated')
