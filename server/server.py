#!/usr/bin/python3
"""
server-app.py
"""
import threading
import socket
import time
import sys
import os

from rdp import rdp
from prquadtree import *

# Global declarations
#TCP_IP = 'localhost'
TCP_HOST = socket.gethostname()  # get local machine name
TCP_HOST_IP = socket.gethostbyname(TCP_HOST)
TCP_PORT = 8000  # set port
BUFFER_SIZE = 1024  # set 1024 bytes as buffer size
EPS = 0.0005

BOX_LIMIT = Box(Point(0,0), 180, 90)

RECEIVED_FILE = 'file_received.txt'
ORIGINAL_DATASET_FILE = 'dataset_original.txt'
REDUCED_DATASET_FILE = 'dataset_reduced.txt'
QUERY_ORIGINAL_DATASET_FILE = 'dataset_original_query.txt'
QUERY_REDUCED_DATASET_FILE = 'dataset_reduced_query.txt'

EXIT_FLAG = False

# create a socket object
SERVER_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# bind to the port
SERVER_SOCKET.bind(("0.0.0.0", TCP_PORT))

# queue up to 5 requests
SERVER_SOCKET.listen(5)


class ServerThread(threading.Thread):
    ''' docstring '''

    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.thread_id = threadID
        self.name = name
        self.client_socket = None
        self.original_qtree = PRQuadTree(BOX_LIMIT)
        self.reduced_qtree = PRQuadTree(BOX_LIMIT)

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
                    #print('Received data = %s', (data))
                    rsize = rsize + len(data)
                    f.write(data)
                    #print(rsize)
                    if rsize >= fsize:
                        print('Breaking from file write')
                        break
            print('Successfully get the file')
            self.process_data()
            self.send_files()
            while True:
                    self.query()
                    self.send_files_2()
            self.client_socket.close()

    def query(self):
        """ docstring """
        msg = self.client_socket.recv(BUFFER_SIZE)
        q_coord = msg.decode('utf-8').split(',')

        for i in range(4):
            q_coord[i] = float(q_coord[i])

        c , hw, hh = box_from_2p(Point(q_coord[0],q_coord[1]),Point(q_coord[2],q_coord[3]))
        q_box = Box(c, hw, hh)
        q_results_original = []
        q_results_tmp = self.original_qtree.query_range(q_box)
        for result in q_results_tmp:
            q_results_original.append([result.x,result.y])

        q_results_reduced = []
        q_results_tmp = self.reduced_qtree.query_range(q_box)
        for result in q_results_tmp:
            q_results_reduced.append([result.x,result.y])

        print(q_results_original)
        print("\n\n\n")
        print(q_results_reduced)

        with open(QUERY_ORIGINAL_DATASET_FILE, 'w') as f:
            print('Storing query original data ...')
            for coord in q_results_original:
                f.write("{},{}\n".format(coord[0], coord[1]))

        with open(QUERY_REDUCED_DATASET_FILE, 'w') as f:
            print('Storing query original data ...')
            for coord in q_results_reduced:
                f.write("{},{}\n".format(coord[0], coord[1]))

    def process_data(self):
        """ docstring """
        lines_buffer = []
        original_dataset = []
        with open(RECEIVED_FILE, 'r') as f:
            lines_buffer = f.readlines()
            #print(lines_buffer)

        for _ in range(6):
            del lines_buffer[0]
        for line in lines_buffer:
            tmp = line.split(',', 2)
            tmp_buffer = float(tmp[0])
            tmp[0] = float(tmp[1])
            tmp[1] = tmp_buffer
            del tmp[2]
            original_dataset.append(tmp)
        #print(original_dataset)

        with open(ORIGINAL_DATASET_FILE, 'w') as f:
            print('Storing original data ...')
            for coord in original_dataset:
                f.write("{},{}\n".format(coord[0], coord[1]))

        reduced_dataset = rdp(original_dataset, EPS)

        with open(REDUCED_DATASET_FILE, 'w') as f:
            print('Storing reduced data ...')
            for coord in reduced_dataset:
                f.write("{},{}\n".format(coord[0], coord[1]))

        for coord in original_dataset:
            self.original_qtree.insert(coord[0],coord[1])

        for coord in reduced_dataset:
            self.reduced_qtree.insert(coord[0],coord[1])
        #print (reduced_qtree.print_all_points(reduced_qtree))

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

    def send_files_2(self):
        """ docstring """
        fsize = os.path.getsize(QUERY_ORIGINAL_DATASET_FILE)
        self.client_socket.send(str(fsize).encode('utf-8'))

        if fsize:
            with open(QUERY_ORIGINAL_DATASET_FILE, 'rb') as f:
                data_buffer = f.read(BUFFER_SIZE)
                while data_buffer:
                    self.client_socket.send(data_buffer)
                    data_buffer = f.read(BUFFER_SIZE)

        fsize = os.path.getsize(QUERY_REDUCED_DATASET_FILE)
        self.client_socket.send(str(fsize).encode('utf-8'))

        if fsize:
            with open(QUERY_REDUCED_DATASET_FILE, 'rb') as f:
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
