import socket
import re

IP = "10.0.42.17"
PORT = 6667

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind((IP, PORT))
serverSocket.listen(5)
print ("Server", IP, "has been set up with PORT:", PORT)

class Client:
    def __init__(self, clientSocket, clientNickname):
        self.clientSocket = clientSocket
        self.clientNickname = clientNickname

clientList = []
lobby = []

def addClientToClientList(socket, message):
    clientOutput = message.split()
    print ("message:", message)
    # ClientOutpu[1] will be equal to the username when this function is called
    print ("ClientOutput[1]:", clientOutput[1])

    newClient = Client(socket, clientOutput[1])
    if not newClient in clientList:
        clientList.append(newClient)
    else:
        print("Error: client socket is already in client list currently")

def addClientToLobby(socket):
    clientInChannel = False
    for client in clientList:
        if client.clientSocket == socket:
            # add client to lobby
            lobby.append(client)
            #socket.send(client.clientNickname +" has joined the Lobby".encode("utf-8"))
            clientInChannel = True
    
    if not clientInChannel:
        socket.send("You are already in this Lobby".encode("utf-8"))
    else:
        for client in lobby:
            client.clientSocket.send((client.clientNickname + " has joined the lobby").encode("utf-8"))
    

  


while True:
    socketConnection, socketAddress = serverSocket.accept()
    print ("accepted socket connection from", socketAddress)
    
    while True:
        message = socketConnection.recv(1024).decode("utf-8")
        print ("Message: ", message)

        # If we receive a Nickname command, we run the code to store a new clientSocket and username
        if re.search("NICK", message):
            print("Adding nickname and socket to socketList")
            addClientToClientList(socketConnection, message)
            

        # If we receive and EXIT command, we run the exit code which removes the client from any channels they are in and then closes the socket
	    if re.search("EXIT", message):
		    print("Disconnecting client socket from:", socketAddress)
 		    break

        if re.search("QUIT", message):
            print("Disconnecting client socket from:", socketAddress)
            break

        # If we receive a JOIN command, we use the socket to search for client in clientList, then add that client to a channel
        if re.search("JOIN", message):
            addClientToLobby(socketConnection)
            

        if message:
            socketConnection.send(message.encode("utf-8"))
            # for x in socketList:
            #     x.send(message.encode("utf-8"))
        else:
            print("Closing socket")
            break

    # # use this for template to send message to everyone in the channel
    # for x in lobby:
    #     messageToSend = x.clientNickname + ">> " + "Hello from the other side\n"
    #     x.clientSocket.send(messageToSend.encode("utf-8"))
        
    print ("closing socketConnection")
    for x in lobby:
        if x.clientSocket == socketConnection:
            lobby.remove(x)

    socketConnection.close()


        # use this for template to send message to everyone in the channel
        # for x in lobby:
        # messageToSend = x.clientNickname + ">> " + "Hello from the other side\n"
        # x.clientSocket.send(messageToSend.encode("utf-8"))
