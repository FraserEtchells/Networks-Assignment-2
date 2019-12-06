import socket
import select
import errno
from time import gmtime, strftime
from datetime import date
import calendar
from threading import Thread


IP = "10.0.42.17"
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

# Prepare username and send them
# We need to encode username to bytes
username = my_username.encode('utf-8')
client_socket.send(username)


def sendMessage():
    while True:
        # Wait for user to input a message
        message = input(f'{my_username} > ')

        # If message is not empty - send it
        if message:
            # Encode message to bytes, prepare header and convert to bytes, like for username above, then send
            message = message.encode('utf-8')
            client_socket.send(message)
    
while True:

	#Begins a thread to run the sendMessage() method to allow messages to be sent and received simultaneously
    sendMessageThread = Thread(target=sendMessage)

    sendMessageThread.start()

    try:
        # Now we want to loop over received messages (there might be more than one) and print them
        while True:

            message = client_socket.recv(1024).decode('utf-8')

		#Splits message into 4 components, First for the sender, Second for the Type of Message, Third for the recipient (channel or username) and Fourth for the remaining input (normally the message)
            messageInput = message.split(' ', 3)
            
            
            #Checks if the received message was from the Lobby and is a bot command, or if  the message was a private message directly to the bot
            if messageInput [2] == "#lobby" and messageInput[1] != "JOIN":
                if messageInput[3] == "!day":
                    #Get today's date
                    dateToday = date.today()
		    #Add "PRIVMSG" command requirements to send the date back to the sender
                    response = 'PRIVMSG ' + messageInput[2] + " " + messageInput[0][1:] + ', today is a ' + calendar.day_name[dateToday.weekday()]
                    #Encode the response then send it back to the server to be parsed and sent to the correct recipient	
                    response = response.encode('utf-8')
                    client_socket.send(response)
                
                elif messageInput[3] == "!time":
                    #get the current local time
                    currentTime = strftime('%H:%M:%S', gmtime())
		    #Add "PRIVMSG" command requirements to send the local time back to the sender
                    response = 'PRIVMSG ' + messageInput[2] + " " + messageInput[0][1:] + ', the local time is: ' + strftime('%H:%M:%S', gmtime())
		    #Encode and send the response to the server to be passed on to the correct recipient
                    response = response.encode('utf-8')
                    client_socket.send(response)

            #If the message was directly sent to the bot, we just send gibberish back to the sender    
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
