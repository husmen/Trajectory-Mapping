#!/usr/bin/python3           # This is server.py file
import threading
import socket
import time
import sys
import os

# Global declarations
#TCP_IP = 'localhost'
TCP_HOST = socket.gethostname() # get local machine name
TCP_PORT = 9999 # set port
BUFFER_SIZE = 1024 # set 1024 bytes as buffer size
FILE_FULL = 'original_file.txt'
FILE_REDUCED = 'new_file.txt'

exitFlag = False

# create a socket object
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# bind to the port
serverSocket.bind((TCP_HOST, TCP_PORT))

# queue up to 5 requests
serverSocket.listen(5)


class serverThread(threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name

    def run(self):
        print("\n*** STARTING SERVER ROUTINE THREAD ***\n")
        while True:
            # establish a connection
            clientSocket, addr = serverSocket.accept()
            currentTime = time.ctime(time.time()) + "\r\n"

            # receive message from client
            msg = clientSocket.recv(1024)

            print("Got a connection request by {} from {} at {}".format(
                msg.decode('ascii'), str(addr), currentTime))

            msgToSend = 'Thank you for connecting, {}'.format(
                msg.decode('ascii')) + "\r\n"
            clientSocket.send(msgToSend.encode('ascii'))

            with open(FILE_FULL, 'wb') as f:
                print('file opened')
                while True:
                    print('receiving data...')
                    data = clientSocket.recv(1024)
                    print('data=%s', (data))
                    if not data:
                        break
                    # write data to a file
                    f.write(data)

            f.close()
            print('Successfully get the file')

            clientSocket.close()

class inputThread(threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    def run(self):
        print("\n*** STARTING INPUT ROUTINE THREAD ***\n")
        flag = True
        while flag:
            try:
                inputCMD = input("your command: ")
                #print(inputCMD)
                if str(inputCMD) == "0":
                    flag = False
                    #exitFlag = True
            except:
                flag = False
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
print("\n*** PROGRAM EXITING ***\n")
#sys.exit(0)
os._exit(0)