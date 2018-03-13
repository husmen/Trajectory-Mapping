#!/usr/bin/python3
"""
server-app.py
"""
import threading
import socket
import time
#import sys
import os

# Global declarations
#TCP_IP = 'localhost'
TCP_HOST = socket.gethostname()  # get local machine name
TCP_PORT = 9999  # set port
BUFFER_SIZE = 1024  # set 1024 bytes as buffer size
FILE_FULL = 'original_file.txt'
FILE_REDUCED = 'new_file.txt'

EXIT_FLAG = False

# create a socket object
SERVER_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# bind to the port
SERVER_SOCKET.bind((TCP_HOST, TCP_PORT))

# queue up to 5 requests
SERVER_SOCKET.listen(5)


class ServerThread(threading.Thread):
    ''' docstring '''
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.thread_id = threadID
        self.name = name

    def run(self):
        ''' docstring '''
        print("\n*** STARTING SERVER ROUTINE THREAD ***\n")
        while True:
            # establish a connection
            client_socket, addr = SERVER_SOCKET.accept()
            current_time = time.ctime(time.time()) + "\r\n"

            # receive message from client
            msg = client_socket.recv(1024)

            print("Got a connection request by {} from {} at {}".format(
                msg.decode('ascii'), str(addr), current_time))

            msg_to_send = 'Thank you for connecting, {}'.format(
                msg.decode('ascii')) + "\r\n"
            client_socket.send(msg_to_send.encode('ascii'))

            with open(FILE_FULL, 'wb') as f:
                print('file opened')
                while True:
                    print('receiving data...')
                    data = client_socket.recv(1024)
                    print('data=%s', (data))
                    if not data:
                        break
                    # write data to a file
                    f.write(data)

            f.close()
            print('Successfully get the file')

            client_socket.close()


class InputThread(threading.Thread):
    ''' docstring '''
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.thread_id = threadID
        self.name = name

    def run(self):
        ''' docstring '''
        print("\n*** STARTING INPUT ROUTINE THREAD ***\n")
        flag = True
        while flag:
            try:
                input_cmd = input("your command: ")
                # print(input_cmd)
                if str(input_cmd) == "0":
                    flag = False
                    #EXIT_FLAG = True
            except:
                flag = False
            else:
                pass
        print("stop command received\n")



if __name__ == "__main__":
    # Create new threads
    SERVER_ROUTINE = ServerThread(1, "Server Routine")
    INPUT_ROUTINE = InputThread(2, "Input Routine")

    # Start new Threads
    SERVER_ROUTINE.start()
    INPUT_ROUTINE.start()

    while INPUT_ROUTINE.isAlive():
        pass

    # wait for threads to end
    SERVER_ROUTINE.join(1)
    print("\n*** PROGRAM EXITING ***\n")
    # sys.exit(0)
    os._exit(0)
