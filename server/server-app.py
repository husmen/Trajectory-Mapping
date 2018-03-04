#!/usr/bin/python3           # This is server.py file
import socket
import time                                         

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

while True:
   # establish a connection
   clientsocket,addr = serversocket.accept()
   currentTime = time.ctime(time.time()) + "\r\n"   

   # receive message from client
   msg = clientsocket.recv(1024)   
   
   print("Got a connection request by {} from {} at {}".format(msg.decode('ascii'), str(addr), currentTime))
    
   msgToSend = 'Thank you for connecting, {}'.format(msg.decode('ascii'))+ "\r\n"
   clientsocket.send(msgToSend.encode('ascii'))
   clientsocket.close()