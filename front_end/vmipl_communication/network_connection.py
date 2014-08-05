import socket

class NetworkConnection ():

	MAX_COMMAND_LENGTH = 5
	MAX_SIZE_LENGTH = 5
	START_COMMAND = "START"
	SEND_OK = "SNDOK"
	SIZE_OK = "SZEOK"

	def __init__(self, sock=None):
		if sock is None:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		else:
			self.sock = sock
			
	def connect(self, host, port):
		self.sock.connect((host, port))

	def close(self):
		self.sock.close()

	def __send(self, message, limit):
		sent = self.sock.send(message[:limit])
		if sent == 0:
			raise RuntimeError("socket connection broken")

	def __receive(self, limit):
		message = self.sock.recv(limit)
		if message == '':
			raise RuntimeError("socket connection broken")
		elif message.strip() == '':
			message = self.__receive(limit)
		return message

	def __send_string(self, string):
		size = str(len(string))
		if len(size) > NetworkConnection.MAX_SIZE_LENGTH:
			max_character_number = 10**NetworkConnection.MAX_SIZE_LENGTH - 1
			raise RuntimeError("max string length of " + 
								str(max_character_number) + " exceeded")
		self.__send(size, NetworkConnection.MAX_SIZE_LENGTH)
		response = self.__receive(NetworkConnection.MAX_COMMAND_LENGTH)
		if response == NetworkConnection.SIZE_OK:
			self.__send(string, len(string))
		else:
			raise RuntimeError("string size was not confirmed")

	def __receive_string(self, confirm_readyness):
		if confirm_readyness:
			self.__send(NetworkConnection.SEND_OK, 
						NetworkConnection.MAX_COMMAND_LENGTH)
		size = self.__receive(NetworkConnection.MAX_SIZE_LENGTH)
		self.__send(NetworkConnection.SIZE_OK, 
					NetworkConnection.MAX_COMMAND_LENGTH)
		return self.__receive(int(size.strip()))

	def __send_command_type(self, command):
		self.__send(command, NetworkConnection.MAX_COMMAND_LENGTH)
	
	def start_vm(self, vm_file_path, vmipl_script):
		self.__send_command_type(NetworkConnection.START_COMMAND)
		send_state = self.__receive(NetworkConnection.MAX_COMMAND_LENGTH)
		if send_state == NetworkConnection.SEND_OK:
			self.__send_string(vm_file_path)
		else:
			raise RuntimeError("server did not allow sending")
		send_state = self.__receive(NetworkConnection.MAX_COMMAND_LENGTH)
		if send_state == NetworkConnection.SEND_OK:
			self.__send_string(vmipl_script)
		else:
			raise RuntimeError("server did not allow sending")
			
	def received_start_command(self):
		command = self.__receive(NetworkConnection.MAX_COMMAND_LENGTH)
		return command == NetworkConnection.START_COMMAND
	
	def get_start_parameters(self):
		vm_file_path = self.__receive_string(True)
		vmipl_script = self.__receive_string(True)
		return vm_file_path, vmipl_script
		
	def receive_server_response(self):
		return self.__receive_string(False)
	
	def send_server_response(self, response):
		self.__send_string(response)
		
		
		
		
		
		
		
		
		
		
		
		
		
