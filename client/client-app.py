#!/usr/bin/python3           # This is client.py file

import socket

# Global declarations
#TCP_IP = 'localhost'
TCP_HOST = socket.gethostname() # get local machine name
TCP_PORT = 9999 # set port
BUFFER_SIZE = 1024 # set 1024 bytes as buffer size
FILE_FULL = 'original_file.txt'
FILE_REDUCED = 'new_file.txt'

# create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connection to hostname on the port.
s.connect((TCP_HOST, TCP_PORT))

# send message to server
msgToSend = 'Houssem'
s.send(msgToSend.encode('ascii'))

# Receive no more than BUFFER_SIZE bytes
msg = s.recv(BUFFER_SIZE)

# print received reply
print(msg.decode('ascii'))

# sending a file
filename = FILE_FULL
f = open(filename, 'rb')
l = f.read(BUFFER_SIZE)
while (l):
    s.send(l)
    print('Sent ', repr(l))
    l = f.read(BUFFER_SIZE)
f.close()
print("\n*** FILE SENDING COMPLETE ***\n")



s.close()
