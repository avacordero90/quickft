#!/usr/bin/env python3

"""
Program: ftserve.py
	Written by: Ava Cordero
	Date: 11/29/2019
	Latest: 12/4/2019

Description:
	A simple file server.

Usage: ftserver portnumber
"""

# imports
import os
import signal
import sys
from socket import *


#Function: conex_data
#Description: Opens a data connection to the client.
#Input: Control socket object.
#Output: Data socket object.
def conex_data(client_socket):
	# set variables
	client_sock_def = client_socket.getsockname()
	client_name = client_sock_def[0]
	client_port = int(sys.argv[1])+1
	
	try:
		# connect to the client
		print("Establishing data connection with client '" + client_name + "' on port " + str(client_port) + "...")
		server_socket = socket(AF_INET, SOCK_STREAM) # create TCP socket
		server_socket.connect((client_name,client_port)) # connect to client
		print("Data connection established with client '" + client_name + "' on port " + str(client_port) + ".")

		# returns the socket
		return server_socket
	except:
		print("Could not establish a data connection with client '" + client_name + "' on port " + str(client_port) + ".")

#Function: ip (Get ip from socket)
#Description: Uses the sockets API to extract the IP Address from a socketobject .
#Input: Data socket object.
#Output: A string including the IP address.
def ip(socket):
	if socket: return socket.getsockname()[0]
	else: return "Unidentified"

#Function: list_dir (List directory contents)
#Description: Opens a data connection to the server, gets and prints directory contents.
#Input: Data socket object.
#Output: None.
def list_dir(socket):
	data = ""
	contents = os.listdir(".")
	for item in contents:
		data += (item + "\n")
	data = data[:-1]
	print("Returning directory contents to " + ip(socket) + ":")
	print(data)
	socket.send(data.encode ("UTF-8")) # send the message

#Function: recv_message(Receive message)
#Description: Receives a message from the other machine.
#Input: Socket and maximum character length for the message.
#Output: String including message.
def recv_cmd(socket, message_max):
	# receive the message back from server
	# must be UTF-8
	try:
		sentence = socket.recv(message_max).decode ("UTF-8")
		if sentence:
			return sentence
	except:
		return

#Function: run_client_srv (Run server-side client)
#Description: Maintains the server-side file transfer functionality.
#Input: Connection socket, server handle, and client handle.
#Output: None.
def run_client_srv(ctrl_socket):
	name = ip(ctrl_socket) # get client IP

	# keep prompting until the message is "\q", or either machine sends a sigint
	while 1:
		msg_in = recv_cmd(ctrl_socket, 4096)
		if msg_in:
			print("Client " + name + " sent command: " + msg_in)
			if msg_in in ("\\q", "\\quit"): # if command is "\q[uit]"
			 	# close connection to client
				print("Control connection to " + name + " closing...")
				ctrl_socket.close() # close control connection
				print("Control connection " + name + " closed.")
				return 1
			elif msg_in.startswith("get "):
								# open new data connection on portnum+1
				data_socket = conex_data(ctrl_socket)

				if data_socket:
					# get filename
					filename = msg_in.split()[1]
					# download file
					send_file(filename, data_socket, ctrl_socket)

					# close socket
					print("Data connection to " + name + " closing...")
					data_socket.close() # close data connection
					print("Data connection to " + name + " closed.")
				else:
					print("Data connection broken, try again or try a different server port.")
			elif msg_in == "list":
				# open new data connection on portnum+1
				data_socket = conex_data(ctrl_socket)

				# get and send server directory contents
				list_dir(data_socket)

				# close socket
				print("Data connection to " + name + " closing...")
				data_socket.close() # close data connection
				print("Data connection to " + name + " closed.")
		else: # otherwise the connection has been closed by a sigint from either machine
			print("Connection to " + name + " closed.")
			return 1

#Function: send_file (Send file to client)
#Description: Opens a data connection to the server and downloads the specified file.
#Input: File name.
#Output: None
def send_file(filename, data_socket, ctrl_socket):
	data = ""
	contents = os.listdir(".") # get dir contents
	if filename in contents: # find file
		print("Sending file " + filename + " to " + ip(data_socket))
		
		# open and read file
		f = open(filename, "r+")
		data = f.read()
		
		# send the length of the file
		ctrl_socket.send(str(len(data)).encode("UTF-8"))

		# send the file in chunks
		x = 0
		while (x in range(0, len(data))):
			data_socket.send(data[x:x+4095].encode ("UTF-8"))
			x += 4096

		# data_socket.send(data.encode ("UTF-8"))
		
		print("File " + filename + "sent to" + ip(data_socket) + ".")
	else:
		connection_socket.send ("0".encode ("UTF-8"))
		print("File " + filename + "not found.")

#Function: start_srv(Start server)
#Description: Starts and maintains the server functionality. Calls the run_client_srv function when a connection is established.
#Input: Port and socket on which to run the server.
#Output: None.
def start_srv(server_port, server_socket):
	print("File server starting ...")
	# always
	while 1:
		# listen for a connection
		print("Listening for a connection on port " + str(server_port) + "...")
		server_socket.listen(1) # wait for an incoming connection
		connection_socket, addr = server_socket.accept() # accept and get socket info
		print("Client connected to server on port " + str(server_port) + "...")
		# keep connection open until message is "\quit"
		stop = 0
		while stop is 0:
			# run the server-based client until stop (0) is returned
			stop = run_client_srv(connection_socket)

# signal handler function
def sig_handle(sig, frame):
	sys.exit(0)


#Function: Main
#Description: Validates arguments, then calls functions to set up the socket, configure the user, and start the server.
#Input: Command line arguments.
#Output: None.
def main ():
	# check that usage is correct
	if len(sys.argv) != 2:
		print("Error: Incorrect usage(chatserve.py serverport).")
		sys.exit(1)
	
	# assign server port and socket
	server_port = int(sys.argv[1]) # port comes from args
	server_socket = socket(AF_INET,SOCK_STREAM) # create socket
	server_socket.bind (("",server_port)) # bind socket to port

	# start server
	start_srv(server_port, server_socket)


# assign signal handler function
signal.signal(signal.SIGINT, sig_handle)

main()