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
    print ("Starting Connecion Message via NICK comand:", message)

    try:
        # ClientOutpu[1] will be equal to the username when this function is called
        print ("ClientOutput[1]:", clientOutput[1])
        

        newClient = Client(socket, clientOutput[1])

        for client in clientList:
            if client.clientNickname == newClient.clientNickname:
                print ("Client username is already in client list")
                return False

        if not newClient in clientList:
            clientList.append(newClient)
        else:
            print("Error: client socket is already in client list currently")
        
        return True
    except:
        print ("Error with general code of addClientToClienList ")
        return True

def addClientToChannel(socket, message):
    clientOutput = message.split()
    try:
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
                        # send a message to everyone in the lobby except the current client
                        if not client.clientSocket == socket:
                         # Get the nickname of the message sender
                            for users in clientList:
                                if users.clientSocket == socket:
                                    # Inform everyone in the channel that a new client has joined
                                    messageToSend = (":" + "server A new client has joined the channel").encode("utf-8")
                                    client.clientSocket.send(messageToSend)
                        # send a message to current client informing them they have joined the channel lobby
                        else:
                            print (":"+client.clientNickname+" "+message)
                            messageToSend = (":" + client.clientNickname + " " + message).encode("utf-8")
                            client.clientSocket.send(messageToSend)
    except:
        print ("Error with trying the general code of addClientToChannel ")

def sendPRIVMSG(socket, message):
    # Process message to see where they are sending message   
    clientOutput = message.split()
    try:
        print ("clientOutput[1]: ", clientOutput[1])

        # If message it to be sent to channel #lobby
        if clientOutput[1] == "#lobby":
            isClientInLobby = False
            # Check to see if client is in lobby
            for client in lobby:
                if client.clientSocket == socket:
                    isClientInLobby = True

            # If client is in #lobby, send the message to everyone else in the lobby
            if isClientInLobby:
                    for client in lobby:
                        if not client.clientSocket == socket:
                            # Get the nickname of the message sender
                            for users in clientList:
                                if users.clientSocket == socket:
                                    # Send message to message recipient
                                    messageToSend = (":" + users.clientNickname + " " + message).encode("utf-8")
                                    client.clientSocket.send(messageToSend)

            
            # Else client is not in channel #lobby
        
        # Else the message must be to a specific user, not a channel
        else:
            for client in clientList:
                # If PRIVMSG recipient's socket is in the clientList, send them the private message
                if client.clientNickname == clientOutput[1]:
                    # Get the nickname of the message sender
                    for users in clientList:
                        if users.clientSocket == socket:
                            # Send message to message recipient
                            messageToSend = (":" + users.clientNickname + " " + message).encode("utf-8")
                            client.clientSocket.send(messageToSend)
    except:
        print ("error in sendPRIVMSG")
    
def leaveChannel(socket, message):
    clientOutput = message.split()
    try:
        if clientOutput[1] == "#lobby":
            for client in lobby:
                if client.clientSocket == socket:
                    lobby.remove(client)
                    print ("Client has been removed from channel ")
    except:
        print ("Error with general code of leaveChannel")

def clientThread(socketConnection, socketAddress):
    while True:
        message = socketConnection.recv(1024).decode("utf-8")
        print ("The raw message before processing it is: ", message)

        # If we receive a Nickname command, we run the code to store a new clientSocket and username
        if re.search("NICK", message):
            print("Adding nickname and socket to socketList")
            # This function is called and if the username is already taken it returns False, causing this socket to be terminated
            if not addClientToClientList(socketConnection, message):
                break
        
        
        # If we receive an EXIT command or QUIT command, we run the exit code which removes the client from any channels they are in and then closes the socket
        if re.search("EXIT", message):
            print("Disconnecting client socket from:", socketAddress)
            break
            
        if re.search("QUIT", message):
            print("Disconnecting client socket from:", socketAddress)
            break

        # If we receive a JOIN command, we use the socket to search for client in clientList, then add that client to a channel
        if re.search("JOIN", message):
            addClientToChannel(socketConnection, message)

        # If we receive a PRIVMSG command, we check if the message is to another client (via username) or to a channel, and then send that message
        if re.search("PRIVMSG", message):
            sendPRIVMSG(socketConnection, message)

        if re.search("PART", message):
            leaveChannel(socketConnection, message)
        
    print ("closing socketConnection")
    for client in lobby:
        if client.clientSocket == socketConnection:
            lobby.remove(client)
    for client in clientList:
        if client.clientSocket == socketConnection:
            clientList.remove(client)

    socketConnection.close()
    return

while True:
    socketConnection, socketAddress = serverSocket.accept()
    print ("accepted socket connection from", socketAddress)

    newClient = True
    for client in clientList:
        if client.clientSocket == socketConnection:
            newClient = False
    
    if newClient:
        newClientThread = threading.Thread(target=clientThread, args=(socketConnection, socketAddress))
        newClientThread.start()

    
    # while True:
    #     message = socketConnection.recv(1024).decode("utf-8")
    #     print ("The raw message before processing it is: ", message)

    #     # If we receive a Nickname command, we run the code to store a new clientSocket and username
    #     if re.search("NICK", message):
    #         print("Adding nickname and socket to socketList")
    #         # This function is called and if the username is already taken it returns False, causing this socket to be terminated
    #         if not addClientToClientList(socketConnection, message):
    #             break
        
        
    #     # If we receive an EXIT command or QUIT command, we run the exit code which removes the client from any channels they are in and then closes the socket
    #     if re.search("EXIT", message):
    #         print("Disconnecting client socket from:", socketAddress)
    #         break
            
    #     if re.search("QUIT", message):
    #         print("Disconnecting client socket from:", socketAddress)
    #         break

    #     # If we receive a JOIN command, we use the socket to search for client in clientList, then add that client to a channel
    #     if re.search("JOIN", message):
    #         addClientToChannel(socketConnection, message)

    #     # If we receive a PRIVMSG command, we check if the message is to another client (via username) or to a channel, and then send that message
    #     if re.search("PRIVMSG", message):
    #         sendPRIVMSG(socketConnection, message)

    #     if re.search("PART", message):
    #         leaveChannel(socketConnection, message)
        
    # print ("closing socketConnection")
    # for client in lobby:
    #     if client.clientSocket == socketConnection:
    #         lobby.remove(client)
    # for client in clientList:
    #     if client.clientSocket == socketConnection:
    #         clientList.remove(client)

    # socketConnection.close()


