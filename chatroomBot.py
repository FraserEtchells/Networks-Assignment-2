import socket
import select
import errno
from time import gmtime, strftime
from datetime import date
import calendar
from threading import Thread

HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 6667

#For the bot, the username should be "nameOfChannel"bot
my_username = input("Username: ")

# Create a socket
# socket.AF_INET - address family, IPv4, some otehr possible are AF_INET6, AF_BLUETOOTH, AF_UNIX
# socket.SOCK_STREAM - TCP, conection-based, socket.SOCK_DGRAM - UDP, connectionless, datagrams, socket.SOCK_RAW - raw IP packets
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to a given ip and port
client_socket.connect((IP, PORT))

# Set connection to non-blocking state, so .recv() call won;t block, just return some exception we'll handle
#client_socket.setblocking(False)

# Prepare username and header and send them
# We need to encode username to bytes, then count number of bytes and prepare header of fixed size, that we encode to bytes as well
username = my_username.encode('utf-8')
username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
client_socket.send(username)

def receiveMessage():
    try:
        while True:
            # Receive our "header" containing username length, it's size is defined and constant
                #username_header = client_socket.recv(1024)

                # If we received no data, server gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
               # if not len(username_header):
                  #  print('Connection closed by the server')
                   # sys.exit()

                # Convert header to int value
               # username_length = int(username_header.decode('utf-8').strip())

                # Receive and decode username
                #username = client_socket.recv(username_length).decode('utf-8')

                # Now do the same for message (as we received username, we received whole message, there's no need to check if it has any length)
                message_header = client_socket.recv(HEADER_LENGTH)
                message_length = int(message_header.decode('utf-8').strip())
                message = client_socket.recv(message_length).decode('utf-8')

                # Print message
                print(f'{username} > {message}')
                
    except IOError as e:
        # This is normal on non blocking connections - when there are no incoming data error is going to be raised
        # Some operating systems will indicate that using AGAIN, and some using WOULDBLOCK error code
        # We are going to check for both - if one of them - that's expected, means no incoming data, continue as normal
        # If we got different error code - something happened
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Reading error: {}'.format(str(e)))
            sys.exit()

        # We just did not receive anything
        #continue

    except Exception as e:
        # Any other exception - something happened, exit
        print('Reading error: '.format(str(e)))
        sys.exit()

def sendMessage():
    while True:
        # Wait for user to input a message
        message = input(f'{my_username} > ')

        # If message is not empty - send it
        if message:
            # Encode message to bytes, prepare header and convert to bytes, like for username above, then send
            message = message.encode('utf-8')
            message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
            client_socket.send(message)
    
while True:
    sendMessageThread = Thread(target=sendMessage)
   # receiveMessageThread = Thread(target=receiveMessage)
    sendMessageThread.start()
    #receiveMessageThread.start()



    # # Wait for user to input a message
    # message = input(f'{my_username} > ')

    # # If message is not empty - send it
    # if message:

    #     # Encode message to bytes, prepare header and convert to bytes, like for username above, then send
    #     message = message.encode('utf-8')
    #     message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
    #     client_socket.send(message_header + message)

    try:
        # Now we want to loop over received messages (there might be more than one) and print them
        while True:

            # Receive our "header" containing username length, it's size is defined and constant
            

            # If we received no data, server gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
           # if not len(username_header):
                #print('Connection closed by the server')
                #sys.exit()

            # Convert header to int value
            

            # Receive and decode username
            #username = client_socket.recv(username_length).decode('utf-8')

            # Now do the same for message (as we received username, we received whole message, there's no need to check if it has any length)
           # message_header = client_socket.recv(HEADER_LENGTH)
            #message_length = int(message_header.decode('utf-8').strip())
            message = client_socket.recv(1024).decode('utf-8')

            
            # Print message
            print(f'{message}')

            messageInput = message.split(' ', 3)
            
            
            #Checks if the received message was from the Lobby and is a bot command, or if  the message was a private message directly to the bot
            if messageInput [2] == "#lobby" and messageInput[1] != "JOIN":
                if messageInput[3] == "!day":
                    #Get today's date and encode it
                    dateToday = date.today()
                    response = 'PRIVMSG ' + messageInput[2] + " " + messageInput[0][1:] + ', today is a ' + calendar.day_name[dateToday.weekday()]

                    print(f"{response}")
                    response = response.encode('utf-8')
                    client_socket.send(response)
                
                elif messageInput[3] == "!time":
                    #get the current local time and encode it
                    currentTime = strftime('%H:%M:%S', gmtime())
                    response = 'PRIVMSG ' + messageInput[2] + " " + messageInput[0][1:] + ', the local time is: ' + strftime('%H:%M:%S', gmtime())

                    response = response.encode('utf-8')
                    client_socket.send(response)

            #If the message was directly sent to the bot       
            elif messageInput[1] == "PRIVMSG":
                    response = 'PRIVMSG ' + messageInput[0][1:] + ' beep boop beep boop'
                    response = response.encode('utf-8')
                    client_socket.send(response)
            
           

    except IOError as e:
        # This is normal on non blocking connections - when there are no incoming data error is going to be raised
        # Some operating systems will indicate that using AGAIN, and some using WOULDBLOCK error code
        # We are going to check for both - if one of them - that's expected, means no incoming data, continue as normal
        # If we got different error code - something happened
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Reading error: {}'.format(str(e)))
            sys.exit()

        # We just did not receive anything
        continue

    except Exception as e:
        # Any other exception - something happened, exit
        print('Reading error: '.format(str(e)))
        sys.exit()
