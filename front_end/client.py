#!/usr/bin/python

import argparse

from vmipl_communication.network_connection import NetworkConnection

def main():
	parser = setup_options_parser()

	# parse given arguments
	args = parser.parse_args()

	validate_input(parser, args)
	port = args.port
	script_content = args.vmipl_script.read()
	args.vmipl_script.close()

	if args.description_file is not None:
		start_vm(args.description_file, script_content, port)
	elif args.vm_id is not None:
		reconfigure_vm(args.vm_id, script_content, port)



def setup_options_parser():
	descr = ("Communicate with execution environment to start virtual" +
					" machine or reconfigure already running one")
	# initialize options parser
	parser = argparse.ArgumentParser(description=descr)

	parser.add_argument("-s", "--start", 
						help=	"start virtual machine given by <VM " + 
								" description file> using the monitoring" +
								" configuration given in <VMI-PL script>", 
								dest="description_file", 
								metavar="<VM description file>")
	parser.add_argument("-r", "--reconfig",
						help=	"reconfigure virtual machine given by <VM Id>"+
								" using the monitoring configuration given in"+
								" <VMI-PL script>", dest="vm_id",
								metavar="<VM Id>")
	parser.add_argument("vmipl_script", help="path to VMI-PL script", 
						type=file, metavar="<VMI-PL script>")
	parser.add_argument("-p", "--port", type=int, default=5555, dest="port",
						help=	"network port to connect to execution" + 
								" environment (default: 5555)")
	return parser

def validate_input(parser, args):
	if args.description_file is not None and args.vm_id is not None:
		parser.error("only one mode can be chosen at a time")
	if args.description_file is None and args.vm_id is None:
		parser.error("at least one mode has to be chosen")

def start_vm(description_file_path, script_content, port):
		
	conn = NetworkConnection()
	conn.connect('127.0.0.1', port)
	
	conn.start_vm(description_file_path, script_content)
	
	response = conn.receive_server_response()
	print response
	
	conn.close()

def reconfigure_vm(vm_id, script_content):
	raise NotImplementedError()

if __name__ == '__main__':
	main()
