#!/usr/bin/python3           # This is client.py file

import socket

# create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

# get local machine name
host = socket.gethostname()                           

port = 9999

# connection to hostname on the port.
s.connect((host, port))

msgToSend = 'Houssem'+ "\r\n" 
s.send(msgToSend.encode('ascii'))                             

# Receive no more than 1024 bytes
msg = s.recv(1024)                                     

s.close()
print (msg.decode('ascii'))