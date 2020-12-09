from client import Client
from server import Server
from common import *
import sys
import json
from socket import *
import threading

if __name__ == "__main__":
    args = sys.argv[1:]

    # client
    if args[0] == "-c":
        if len(args) != 5:
            print("wrong number of arguments")
            sys.exit()
        try:
            username, server_ip, server_port, client_port = args[1], args[2], int(args[3]), int(args[4])
        except ValueError:
            argument_error()

        # create a client
        client = Client(username,server_ip,server_port,client_port)

        # thread for listening msg from the socket
        # the main thread is used for keyboard input
        listen_thread = threading.Thread(target=client.listen_chat, args=(), daemon=True)
        listen_thread.start()

        while True:
            msg = input(">>> ")
            msg_list = msg.split(' ')
            try:
                if msg_list[0] != "send" and msg_list[0] != "dereg" and msg_list[0] != "reg":
                    print("wrong format of input!")
                    continue
                if msg_list[1] not in client.client_status:
                    print("the receiver is not registered!")
                    continue

            except IndexError:
                print("wrong format of sending message!")
                continue
            if msg_list[0] == "send":
                msg = ' '.join(msg_list[2:])
                if not client.client_status[msg_list[1]]['online']:
                    client.send_server(msg_list[1],msg)
                else:
                    client.send_msg(msg_list[1],msg)
            elif msg_list[0] == "dereg":
                if msg_list[1] != client.username:
                    print("you cannot deregister other users!")
                    continue
                client.dereg(msg)
            elif msg_list[0] == "reg":
                if msg_list[1] != client.username:
                    print("you cannot register other users!")
                    continue
                client.rereg(msg)


    # server
    elif args[0] == "-s":
        if len(args) != 2:
            print("wrong number of arguments")
            sys.exit()
        try:
            server_port = int(args[1])
        except ValueError:
            argument_error()
        server = Server(server_port)

        # listen to message from the socket
        while True:
            message, clientAddress = server.serverSocket.recvfrom(2048)
            message = message.decode('utf-8')
            if message.startswith("register"):
                message = message.split(' ')
                username = message[1]
                if username in server.clientStatus:
                    # print("error")
                    msg = "error: this username has already registered, choose another one!"
                    server.serverSocket.sendto(msg.encode(),clientAddress)
                else:
                    server.reg(username,clientAddress)
            elif message.startswith("dereg"):
                message = message.split(' ')
                username = message[1]
                server.dereg(username,clientAddress)

            elif message.startswith("send"):
                server.receive_msg(message,clientAddress)

            elif message.startswith("reg"):
                server.rereg(message,clientAddress)

            elif message.startswith("ACK"):
                server.ack = True


    else:
        print("wrong mode")
        sys.exit()

    
    
