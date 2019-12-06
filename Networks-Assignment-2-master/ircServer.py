import socket
import re
import threading

# Set IP and PORT (should be set to LAB computer virtual machine IP 10.0.42.17)
IP = "10.0.42.17"
PORT = 6667

# Create the server socket and let it listen for client sockets
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind((IP, PORT))
serverSocket.listen(5)
print ("Server", IP, "has been set up with PORT:", PORT)

# Here we create a simple client class where each instance will be a client object holding their socket and nickname
class Client:
    def __init__(self, clientSocket, clientNickname):
        self.clientSocket = clientSocket
        self.clientNickname = clientNickname

# We create a client list for all the client's connected
clientList = []
# We create a channel called test which will hold clients as they join
test = []

# addClientToClientList
# Params: socket - socket of the client to add, message - the command message received by the client socket
# Usage: Creates a new client object based on a received client socket and nickname, then stoes that client in clientList
def addClientToClientList(socket, message):
    clientOutput = message.split()
    print ("Starting Connecion Message via NICK comand:", message)

    try:
        # ClientOutpu[1] will be equal to the username when this function is called
        print ("ClientOutput[1]:", clientOutput[1])
        newClient = Client(socket, clientOutput[1])

        # Check that the clientNickname isn't already in clientList
        for client in clientList:
            if client.clientNickname == newClient.clientNickname:
                print ("Client username is already in client list")
                return False

        # add the new client to clientList
        if not newClient in clientList:
            clientList.append(newClient)
        # return an error stating that client is already in the list
        else:
            print("Error: client socket is already in client list currently")
        
        return True
    # Throw an exception if there is a fault with addClientToClientList call
    except:
        print ("Error with general code of addClientToClienList ")
        return True

# addClientToChannel
# Params: socket - socket of the client to add, message - the command message received by the client socket
# Usage: Finds a client from the clientList based on the socket parameter, and then adds that client to a channel 
# (specifically the test channel in this case)
def addClientToChannel(socket, message):
    clientOutput = message.split()
    try:
        # ClientOutput[1] will be equal to the second index of message i.e. the name of the channel
        print ("ClientOutput[1]:", clientOutput[1] + "\n")

        # For each client
        for client in clientList:
            # If client is the client whose socket we passed into the parameter i.e. the client who called this command
            if client.clientSocket == socket:
                # If client who called this command is already in channel, inform them as such
                if client in test:
                    print ("Client is already in test")
                    client.clientSocket.send((client.clientNickname + " is already in the test \n").encode("utf-8"))
                    break
                # Add client who called this command to channel test
                else:
                    print ("Adding client to test")
                    test.append(client)
                    # Inform client that they are now part of the test channel; go through clients in test to do this
                    for client in test:
                        if client.clientSocket == socket:
                            messageToSend = (":" + client.clientNickname + " " + message).encode("utf-8")
                            client.clientSocket.send(messageToSend)
    except:
        print ("Error with trying the general code of addClientToChannel ")

# sendPRIVMSG
# Params: socket - socket of the client to add, message - the command message received by the client socket
# Usage: client (socket) calls this command to either send a message to the channel they are in or to another client 
def sendPRIVMSG(socket, message):
    # Process message to see where they are sending message   
    clientOutput = message.split()
    try:
        print ("clientOutput[1]: ", clientOutput[1])

        # If message it to be sent to channel #test
        if clientOutput[1] == "#test":
            isClientInLobby = False
            # Check to see if client is in test
            for client in test:
                if client.clientSocket == socket:
                    isClientInLobby = True

            # If client is in #test, send the message to everyone else in the test
            if isClientInLobby:
                for client in test:
                    if not client.clientSocket == socket:
                        # Get the nickname of the message sender
                        for users in clientList:
                            if users.clientSocket == socket:
                                # Send message to message recipient
                                messageToSend = (":" + users.clientNickname + " " + message).encode("utf-8")
                                client.clientSocket.send(messageToSend)

            
            # Else client is not in channel #test
        
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

# leaveChannel
# Params: socket - socket of the client to add, message - the command message received by the client socket
# Usage: client who calls this command leaves the channel they are currently in
def leaveChannel(socket, message):
    clientOutput = message.split()
    try:
        # if the channel they wish to leave is the #test channel
        if clientOutput[1] == "#test":
            # for each client in channel test
            for client in test:
                # if client is the client(socket) who called the commmand, remove the from the channel and inform them as such
                if client.clientSocket == socket:
                    messageToSend = (":" + client.clientNickname + " " + message).encode("utf-8")
                    client.clientSocket.send(messageToSend)
                    test.remove(client)
                    print ("Client has been removed from channel ")
            
    except:
        print ("Error with general code of leaveChannel")

# clientThread
# Params: socketConnection - the socket of a connecting client, socketAddress - the address of a connecting client
# Usage: Main loop code of each client. Each client will have their own instance of clientThread, ran through a thread, which
# receives and parses a message received from a client, and calls code based on the command sent in the message.
def clientThread(socketConnection, socketAddress):
    while True:
        # Receive message from client
        message = socketConnection.recv(1024).decode("utf-8")
        print ("The raw message before processing it is: ", message)

        # If we receive a Nickname command, we run the code to store a new clientSocket and username
        if re.search("NICK", message):
            print("Adding nickname and socket to socketList")
            # This function is called and if the username is already taken it returns False, causing this socket to be terminated
            if not addClientToClientList(socketConnection, message):
                break
        
        
        # If we receive an EXIT command or QUIT command, we run the exit code which removes the client from any channels they are in and then closes the socket
        elif re.search("EXIT", message):
            print("Disconnecting client socket from:", socketAddress)
            break
            
        elif re.search("QUIT", message):
            print("Disconnecting client socket from:", socketAddress)
            break

        # If we receive a JOIN command, we use the socket to search for client in clientList, then add that client to a channel
        elif re.search("JOIN", message):
            addClientToChannel(socketConnection, message)

        # If we receive a PRIVMSG command, we check if the message is to another client (via username) or to a channel, and then send that message
        elif re.search("PRIVMSG", message):
            sendPRIVMSG(socketConnection, message)

        # If we receive a PART command, we use the socket to search for the client in a channel (speicifed by message), and then remove client 
        # from said channel
        elif re.search("PART", message):
            leaveChannel(socketConnection, message)
    
    # This code is run once a client Breaks from the general loop via a close command or already taken nickname
    print ("closing socketConnection")
    # Remove the client from test channel if they exist in it
    for client in test:
        if client.clientSocket == socketConnection:
            test.remove(client)
    # Remove the client from clientList if they exist in it
    for client in clientList:
        if client.clientSocket == socketConnection:
            clientList.remove(client)
    # Close the socket connection to client
    socketConnection.close()
    return

# Main loop
while True:
    # Receive and accept a socket connection from a client
    socketConnection, socketAddress = serverSocket.accept()
    print ("accepted socket connection from", socketAddress)

    # Check accpeted client is not already in the clientList and thus already connected
    newClient = True
    for client in clientList:
        if client.clientSocket == socketConnection:
            newClient = False
    
    # Start a client thread for the new client if they are not already connected to the server
    if newClient:
        newClientThread = threading.Thread(target=clientThread, args=(socketConnection, socketAddress))
        newClientThread.start()

    


