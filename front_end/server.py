#!/usr/bin/python

import argparse
import os
import signal
import socket
import sys

from vmipl_server.connection_handler import ConnectionHandler

def main():
	running_vms = {}
	parser = setup_options_parser()
	
	# parse given arguments
	args = parser.parse_args()
	
	if os.getuid() != 0:
		parser.error(	"This program requires root privileges. Please run" + 
						" again with necessary permissions.")
	
	uid = os.stat(parser.prog).st_uid
	os.seteuid(uid)
	
	port = args.port
	qemu_path = args.qemu_path
	pipes_directory = os.path.dirname(os.path.abspath(__file__)) + '/pipes'
	
	if not os.path.exists(pipes_directory):
		os.makedirs(pipes_directory)
	
	serversocket = setup_serversocket(uid, port)
	serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	def signal_handler(signal, frame):
		serversocket.close()
		# terminate all receivers
		for channel in running_vms:
			running_vms[channel][1].running = False
		print "\nServer shutdown"
		sys.exit()
	
	signal.signal(signal.SIGINT, signal_handler)

	start_server(serversocket, running_vms, qemu_path, pipes_directory)
	
	
	
def setup_options_parser():
	descr = ("Execution environment for VMI-PL")
	# initialize options parser
	parser = argparse.ArgumentParser(description=descr)
	
	parser.add_argument("-p", "--port", type=int, default=5555, dest="port",
						help=	"network port to connect to execution" + 
								" environment (default: 5555)")
	parser.add_argument("-q", "--qemu", type=str, default='qemu', 
						dest="qemu_path", 
						help= 	"path to the qemu executable to use by the" +
								" execution environment (default: qemu)")
	return parser

def setup_serversocket(uid, port):

	serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	serversocket.bind(('127.0.0.1', port))
	serversocket.listen(5)
	
	return serversocket

def start_server(serversocket, running_vms, qemu_path, pipes_directory):
	while True:
		(clientsocket, address) = serversocket.accept()
		handler = ConnectionHandler(clientsocket, running_vms, 
												qemu_path, pipes_directory)
		handler.start()
		
if __name__ == '__main__':
	main()


