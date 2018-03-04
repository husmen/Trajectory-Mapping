#!/usr/bin/python3           # This is server.py file
import threading
import socket
import time
import sys
import os

exitFlag = False

# create a socket object
serversocket = socket.socket(
	        socket.AF_INET, socket.SOCK_STREAM)

# get local machine name
host = socket.gethostname()

port = 9999

# bind to the port
serversocket.bind((host, port))

# queue up to 5 requests
serversocket.listen(5)


class serverThread(threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name

    def run(self):
        print("Starting server routine thread")
        while True:
            # establish a connection
            clientsocket, addr = serversocket.accept()
            currentTime = time.ctime(time.time()) + "\r\n"

            # receive message from client
            msg = clientsocket.recv(1024)

            print("Got a connection request by {} from {} at {}".format(
                msg.decode('ascii'), str(addr), currentTime))

            msgToSend = 'Thank you for connecting, {}'.format(
                msg.decode('ascii')) + "\r\n"
            clientsocket.send(msgToSend.encode('ascii'))
            clientsocket.close()

class inputThread(threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    def run(self):
        print("Starting input routine thread")
        flag = True
        while flag:
            inputCMD = input("your command: ")
            print(inputCMD)
            if str(inputCMD) == "0":
                flag = False
                #exitFlag = True
            else:
                pass
        print("stop command received\n")        

# Create new threads
serverRoutine = serverThread(1, "Server Routine")
inputRoutine = inputThread(2, "Input Routine")

# Start new Threads
serverRoutine.start()
inputRoutine.start()

while inputRoutine.isAlive():
    pass

# wait for threads to end
serverRoutine.join(1)
print("program exiting\n")
#sys.exit(0)
os._exit(0)