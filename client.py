import sys
import json
from socket import *
import time
import uuid

class Client:
    def __init__(self,username,server_ip,server_port,client_port):
        self.username = username
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_port = client_port
        self.clients_status = {}
        self.unacked_msg = {}
        self.deregAck = False


        # register
        self.clientSocket = socket(AF_INET,SOCK_DGRAM)
        self.clientSocket.bind(('', self.client_port))
        message = f"register: {self.username}"
        self.clientSocket.sendto(message.encode(),(self.server_ip,self.server_port))
        rec_msg, _ = self.clientSocket.recvfrom(2048)
        rec_msg_decode = rec_msg.decode('utf-8')
        if rec_msg_decode.startswith("error"):
            # print("got error")
            print(rec_msg_decode)
            sys.exit()
        self.client_status = json.loads(rec_msg.decode())
        print(">>> [Welcome, You are registered.]")
        print(">>> [Client table updated.]")
        # for test
        # for k,v in self.client_status.items():
        #     print(k,v)

    # listen message from the socket
    def listen_chat(self):
        while True:
            rec_msg, sender_addr = self.clientSocket.recvfrom(2048)
            ip,port = sender_addr

            # msg from server
            if ip == self.server_ip and port == self.server_port:
                rec_msg = rec_msg.decode()
                if rec_msg.startswith("ACK"):
                    self.deregAck = True
                    print("\n>>> [You are Offline. Bye.]")
                elif rec_msg.startswith("offlineACK"):
                    msg_list = rec_msg.split(' ')
                    ack_uid = msg_list[1]
                    self.unacked_msg[ack_uid] = True
                elif rec_msg.startswith("rereg"):
                    msg_list = rec_msg.split(' ')
                    msg = ' '.join(msg_list[1:])
                    print(f"\n>>> {msg}")
                    print(">>>", end=' ', flush=True)
                # elif rec_msg.startswith("error"):
                #     print("got error")
                #     print(rec_msg)
                #     sys.exit()
                else:
                    self.client_status = json.loads(rec_msg)
                    print("\n>>> [Client table updated.]")
                    print(">>>", end=' ',flush=True)


            # msg from other clients
            else:
                rec_msg = rec_msg.decode()
                # print(rec_msg)
                rec_msg = rec_msg.split(' ')
                # chat msg
                if rec_msg[0] == "send":
                    sender = rec_msg[1]
                    ack_uid = rec_msg[2]
                    msg = ' '.join(rec_msg[3:])
                    print(f"\n>>> client {sender}: {msg}")
                    print(">>>", end=' ',flush=True)
                    ack = "ACK " + ack_uid
                    self.clientSocket.sendto(ack.encode(), sender_addr)
                # ack msg
                elif rec_msg[0] == "ACK":
                    ack_uid = rec_msg[1]
                    self.unacked_msg[ack_uid] = True


    def send_msg(self,receiver,msg):
        recv_addr = self.client_status[receiver]['ip'],self.client_status[receiver]['port']
        uid = str(uuid.uuid4())
        n_msg = f"send {self.username} {uid} {msg}"

        self.clientSocket.sendto(n_msg.encode(),recv_addr)
        self.unacked_msg[uid] = False
        # wait for 500msec
        time.sleep(0.5)
        if not self.unacked_msg[uid]:
            print(f">>> [No ACK from {receiver}, message sent to server.]")
            self.send_server(receiver,msg)
            del self.unacked_msg[uid]
        else:
            print(f"[Message received by {receiver}.]")

    # if client does not respond, send msg to the server
    def send_server(self,receiver,msg):
        recv_addr = self.server_ip,self.server_port
        uid = str(uuid.uuid4())
        # c_time = str(time.ctime())
        msg = f"send {self.username} {receiver} {uid} {msg}"

        self.unacked_msg[uid] = False
        # wait for 500msec
        i = 0
        while not self.unacked_msg[uid] and i<5:
            self.clientSocket.sendto(msg.encode(), recv_addr)
            time.sleep(1)
            # print("send")
            if self.unacked_msg[uid]:
                print(">>> [Messages received by the server and saved]")
                return
            i += 1
            # print(uid)
        print(f">>> [No ACK from the server.]")
        sys.exit()


    def rereg(self,msg):
        serverAddr = self.server_ip, self.server_port
        self.clientSocket.sendto(msg.encode(),serverAddr)
        self.deregAck = False


    def dereg(self,msg):
        serverAddr = self.server_ip, self.server_port
        i = 0
        while not self.deregAck and i<5:
            self.clientSocket.sendto(msg.encode(),serverAddr)
            time.sleep(0.5)
            i += 1
        if not self.deregAck:
            print("\n>>> [Server not responding]")
            print(">>> [Exiting]")
            sys.exit()



    







