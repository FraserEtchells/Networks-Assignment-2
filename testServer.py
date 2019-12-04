import socket
import re
import threading

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

def addClientToChannel(socket, message):
    clientOutput = message.split()
    print ("ClientOutput[0]", clientOutput[0] + "\n")
    print ("ClientOutput[1]:", clientOutput[1] + "\n")


    for client in clientList:
        if client.clientSocket == socket:
            if client in lobby:
                print ("Client is already in lobby")
                client.clientSocket.send((client.clientNickname + " is already in the lobby \n").encode("utf-8"))
                break
            else:
                print ("Adding client to lobby")
                lobby.append(client)
                for client in lobby:
                    print (":"+client.clientNickname+" "+message)
                    messageToSend = (":" + client.clientNickname + " " + message).encode("utf-8")
                    client.clientSocket.send(messageToSend)

def sendPRIVMSG(socket, message):
    # Process message to see where they are sending message   
    clientOutput = message.split()
    print ("clientOutput[1]: ", clientOutput[1])

    # If message it to be sent to channel #Lobby
    if clientOutput[1] == "#lobby":
        isClientInLobby = False
        # Check to see if client is in lobby
        for client in lobby:
            if client.clientSocket == socket:
                isClientInLobby = True

        # If client is in #Lobby, send the message to everyone else in the lobby
        if isClientInLobby:
                for client in lobby:
                    print ("We even get here to the sending of a client lobby PRIVMSG!")
                    #if not client.clientSocket == socket:
                    messageToSend = (":" + client.clientNickname + " " + message).encode("utf-8")
                    client.clientSocket.send(messageToSend)
        
        # Else client is not in channel #Lobby
    
    # Else the message must be to a specific user, not a channel
    else:
        for client in clientList:
            # If PRIVMSG recipient's socket is in the clientList, send them the private message
            if client.clientNickname == clientOutput[1]:
                messageToSend = (":" + client.clientNickname + " " + message).encode("utf-8")
                client.clientSocket.send(messageToSend)
    
    


    

  


while True:
    socketConnection, socketAddress = serverSocket.accept()
    print ("accepted socket connection from", socketAddress)
    
    while True:
        message = socketConnection.recv(1024).decode("utf-8")
        print ("The raw message before processing it is: ", message)

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
            addClientToChannel(socketConnection, message)

        if re.search("PRIVMSG", message):
            sendPRIVMSG(socketConnection, message)
            

        # if message:
        #     socketConnection.send(message.encode("utf-8"))
        #     # for x in socketList:
        #     #     x.send(message.encode("utf-8"))
        # else:
        #     print("Closing socket")
        #     break

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
