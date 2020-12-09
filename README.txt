Jiawei Zhang jz3209

To start a server with port number 10001, run command
python3 udpchat.py -s 10001
To start a client with username a, port number 20000, and connect to the server, run command
python3 udpchat.py -c a 127.0.0.1 10001 20000


structure of the folder:
client.py implements client class and server.py implements server class
udpchat.py is the main program, and common.py stores a common function used by other files.


For client:
To deregister a client, input "dereg <username>"
To send message to client with username b, input "send b <message>"
To reregister a client, input"reg <username>"
client class is implemented in client.py,
the main thread for client is to accept keyboard input.
The client also starts another thread to receive messages from the socket.
The client distinguishes messages by checking where this message comes from and
the first word in each message. For example, chat message starts with "send",
ack message starts with "ACK". "ACK" message from another client and "ACK" from the
server can be distinguished by checking who sends this message.


For server:
server class is implemented in server.py, client status is maintained in a dictionary.
The key is the username of the client, the value is another dictionary which contains information
of the ip, port, and online status of the associated client.
The server distinguishes messages by checking the first word in each message.
redirected chat message starts with "send", register message starts with "register", dereg message
starts with "dereg".
The server stores offline chat messages in files, each client has its own file of offline chat
messages. The file is created when a client want to send message to the offline client and find that
there is no file for this offline client. Once the client reregisters, the corresponding file is read 
and messages will be sent to the client. Then the file is deleted. It will be created again if the client
goes offline again and someone wants to send him/her messages.




