import socket
import re

IP = "127.0.0.1"
PORT = 6667

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind((IP, PORT))
serverSocket.listen(5)
print ("Server", IP, "has been set up with PORT:", PORT)

class Client:
    def __init__(self, clientSocket, clientNickname):
        self.clientSocket = clientSocket
        self.clientNickname = clientNickname

socketList = []
lobby = []

def addClientToChannel(socket, message):
    clientOutput = message.split()
    print ("message:", message)
    print ("ClientOutput[1]:", clientOutput[1])

    newClient = Client(socket, clientOutput[1])
    lobby.append(newClient)

  


while True:
    socketConnection, socketAddress = serverSocket.accept()
    if not socketConnection in socketList:
        print ("Adding a new socket to list")
        socketList.append(socketConnection)
    print ("accepted socket connection from", socketAddress)
    
    while True:
        message = socketConnection.recv(1024).decode("utf-8")
        print ("Message: ", message)
        if re.search("NICK", message):
            print("Adding nickname and socket to socketList")
            addClientToChannel(socketConnection, message)
            break

        if message:
            socketConnection.send(message.encode("utf-8"))
            # for x in socketList:
            #     x.send(message.encode("utf-8"))
        else:
            print("Closing socket")
            break

    # use this for template to send message to everyone in the channel
    for x in lobby:
        messageToSend = x.clientNickname + ">> " + "Hello from the other side\n"
        x.clientSocket.send(messageToSend.encode("utf-8"))
        
    print ("closing socketConnection")
    socketConnection.close()

        # use this for template to send message to everyone in the channel
        # for x in lobby:
        # messageToSend = x.clientNickname + ">> " + "Hello from the other side\n"
        # x.clientSocket.send(messageToSend.encode("utf-8"))