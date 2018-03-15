#!/usr/bin/python3
"""
server-app.py
"""
import threading
import socket
import time
#import sys
import os

from rdp import rdp

# Global declarations
#TCP_IP = 'localhost'
TCP_HOST = socket.gethostname()  # get local machine name
TCP_HOST_IP = socket.gethostbyname(TCP_HOST)
TCP_PORT = 9999  # set port
BUFFER_SIZE = 1024  # set 1024 bytes as buffer size
EPS = 0.001

RECEIVED_FILE = 'file_received.txt'
ORIGINAL_DATASET_FILE = 'dataset_original.txt'
REDUCED_DATASET_FILE = 'dataset_reduced.txt'

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
        self.client_socket = None

    def run(self):
        ''' docstring '''
        print("\n*** STARTING SERVER ROUTINE THREAD ***\n")
        print("Hostname: {}\n".format(TCP_HOST))
        print("Host IP: {}\n".format(TCP_HOST_IP))
        while True:
            # establish a connection
            self.client_socket, addr = SERVER_SOCKET.accept()
            current_time = time.ctime(time.time()) + "\r\n"

            # receive message from client
            msg = self.client_socket.recv(BUFFER_SIZE)

            print("Got a connection request by {} from {} at {}".format(
                msg.decode('utf-8'), str(addr), current_time))

            msg_to_send = 'Thank you for connecting, {}'.format(
                msg.decode('utf-8')) + "\r\n"
            self.client_socket.send(msg_to_send.encode('utf-8'))

            with open(RECEIVED_FILE, 'wb') as f:
                print('Receiving data ...')
                msg = self.client_socket.recv(BUFFER_SIZE)
                fsize = int(msg.decode('utf-8'))
                rsize = 0
                while True:
                    data = self.client_socket.recv(BUFFER_SIZE)
                    print('Received data = %s', (data))
                    rsize = rsize + len(data)
                    f.write(data)
                    #fsize_current = os.path.getsize(RECEIVED_FILE)
                    print(rsize)
                    if rsize >= fsize:
                        print('Breaking from file write')
                        break
            print('Successfully get the file')
            self.process_data()
            self.send_files()
            self.client_socket.close()

    def process_data(self):
        """ docstring """
        lines_buffer = []
        original_dataset = []
        with open(RECEIVED_FILE, 'r') as f:
            lines_buffer = f.readlines()
            print(lines_buffer)

        for _ in range(6):
            del lines_buffer[0]
        for line in lines_buffer:
            tmp = line.split(',', 2)
            tmp[0] = float(tmp[0])
            tmp[1] = float(tmp[1])
            del tmp[2]
            original_dataset.append(tmp)
        print(original_dataset)

        with open(ORIGINAL_DATASET_FILE, 'w') as f:
            print('Storing original data ...')
            for coord in original_dataset:
                f.write("{},{}\n".format(coord[0], coord[1]))

        reduced_dataset = rdp(original_dataset, EPS)

        with open(REDUCED_DATASET_FILE, 'w') as f:
            print('Storing reduced data ...')
            for coord in reduced_dataset:
                f.write("{},{}\n".format(coord[0], coord[1]))

    def send_files(self):
        """ docstring """
        fsize = os.path.getsize(ORIGINAL_DATASET_FILE)
        self.client_socket.send(str(fsize).encode('utf-8'))

        with open(ORIGINAL_DATASET_FILE, 'rb') as f:
            data_buffer = f.read(BUFFER_SIZE)
            while data_buffer:
                self.client_socket.send(data_buffer)
                data_buffer = f.read(BUFFER_SIZE)

        fsize = os.path.getsize(REDUCED_DATASET_FILE)
        self.client_socket.send(str(fsize).encode('utf-8'))

        with open(REDUCED_DATASET_FILE, 'rb') as f:
            data_buffer = f.read(BUFFER_SIZE)
            while data_buffer:
                self.client_socket.send(data_buffer)
                data_buffer = f.read(BUFFER_SIZE)



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
            except KeyboardInterrupt:
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
