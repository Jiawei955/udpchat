import sys
import json
from socket import *
import os
import time


class Server:
    def __init__(self,port):
        self.port = port
        self.serverSocket = socket(AF_INET,SOCK_DGRAM)
        self.serverSocket.bind(('',self.port))
        self.clientStatus = {}
        self.ack = False


    def reg(self,username,clientAddress):
        ip,port = clientAddress
        # print(clientAddress)
        # print(type(ip),type(port))
        client_info = {
            "ip": ip,
            "port": port,
            "online": True,
        }
        self.clientStatus[username] = client_info

        self.broadcast_table()

        return

    def dereg(self,username,clientAddress):
        self.clientStatus[username]['online'] = False
        self.broadcast_table()
        ack = "ACK dereg"
        self.serverSocket.sendto(ack.encode(), clientAddress)

    # handle the message from the client to an offline client. store these message
    # in the corresponding file
    def receive_msg(self,msg,sender_addr):
        # print("offline")
        msg = msg.split(' ')
        sender = msg[1]
        receiver = msg[2]
        ackuid = msg[3]
        message = ' '.join(msg[4:])
        c_time = str(time.ctime())
        if self.clientStatus[receiver]['online'] and self.check_exist(receiver):
            err_msg = f"\n>>> [Client {receiver} exists!!]"
            self.ack = False
            self.serverSocket.sendto(err_msg.encode(),sender_addr)
            return
        if self.clientStatus[receiver]["online"]:
            self.clientStatus[receiver]["online"] = False
            self.broadcast_table()
        with open(f"{receiver}","a") as f:
            text = f">>> {sender}: {c_time} {message}\n"
            f.write(text)
        ack = "offlineACK " + ackuid
        self.serverSocket.sendto(ack.encode(),sender_addr)

    def rereg(self,msg,client_addr):
        msg_list = msg.split(' ')
        rereg_client = msg_list[1]
        # recv_addr = self.clientStatus[rereg_client]['ip'],self.clientStatus[rereg_client]['port']
        # print("rereg")
        if os.path.exists(f"{rereg_client}"):
            with open(f"{rereg_client}","r") as f:
                msg = f.read()
                msg = "rereg You Have Messages:\n" + msg
                self.serverSocket.sendto(msg.encode(),client_addr)
            os.remove(f"{rereg_client}")
        self.clientStatus[rereg_client]["online"] = True
        self.broadcast_table()

    # broadcast the updated table to clients
    def broadcast_table(self):
        for k in self.clientStatus:
            if self.clientStatus[k]['online']:
                c_address = self.clientStatus[k]['ip'],self.clientStatus[k]['port']
                self.serverSocket.sendto(json.dumps(self.clientStatus).encode(), c_address)

    # check if a client is active or offline
    def check_exist(self,client):
        n_msg = f"send server are you there"
        recv_addr = self.clientStatus[client]['ip'],self.clientStatus[client]['port']
        self.serverSocket.sendto(n_msg.encode(), recv_addr)
        time.sleep(1)
        return self.ack

        

        

