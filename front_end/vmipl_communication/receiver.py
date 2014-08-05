import os
import struct
import socket
import threading

from vmipl_aux.constants import Constants

from vmipl_communication.connection import Connection

class Receiver (threading.Thread):

	@staticmethod
	def is_file(output_channel):
		return not output_channel.startswith('#')

	def __init__(self, channel_number, group_id, file_path, euid):
		threading.Thread.__init__(self)
		self.channel_number = channel_number
		self.group_id = group_id
		self.file_path = file_path
		self.euid = euid
		self.running = True

	def convert_to_hex_string(self, byte_stream):
		string = ''
		for byte in byte_stream:
			num = struct.unpack('B', byte)[0]
			string += hex(num) + ' '
		return string

	def get_string_length(self, string):
		length = 0
		for i in string:
			if i == '\0':
				break
			else:
				length += 1
		return length		
		
	def process_proc_list_message(self, payload):
		event_id = struct.unpack('L', payload[:4])
		fields = struct.unpack('B', payload[4])
		content = (str(event_id[0]) + ': ' + str(Constants.vmipl_msg_d_proc_list) 
						+ ': ' + str(fields[0]) + ': ')
		start_index = 5
		if fields[0] & Constants.vmipl_pid:
			pid = struct.unpack('L', payload[start_index:start_index + 4])
			content += str(pid[0]) + ': '
			start_index += 4
		if fields[0] & Constants.vmipl_name:
			length = self.get_string_length(payload[start_index:])		
			name = struct.unpack(str(length) + 's', payload[start_index:
														start_index + length])
			content += name[0] + ': '
			start_index += length + 1
		if fields[0] & Constants.vmipl_pgdp:
			pgd = struct.unpack('L', payload[start_index:start_index + 4])
			content += str(hex(pgd[0])) + ': '
			start_index += 4
		if fields[0] & Constants.vmipl_path:
			length = self.get_string_length(payload[start_index:])
			path = struct.unpack(str(length) + 's', payload[start_index:
														start_index + length])
			content += path[0] + ': '
		return content[:-2]
		
		
	def process_message(self, message, output_file):
		if message.type == Constants.vmipl_msg_d_proc_list:
			content = self.process_proc_list_message(message.payload) + '\n'
		elif message.type == Constants.vmipl_msg_d_proc_list_end:
			content = '-------------------------------------------------\n'
		elif message.type == Constants.vmipl_msg_e_net:
			content = message.payload
		else:
			event_id, key = struct.unpack('LL', message.payload[:8])
			if message.type == Constants.vmipl_msg_d_read_mem:
				key = hex(key)
			content = ''
	#		content = str(message.msglen) + ': ' + repr(message.payload) + '\n'
			content += (str(event_id) + ': ' + str(message.type) + ': ' + str(key)
							+ ': ' 
							+ self.convert_to_hex_string(message.payload[8:]) 
							+ '\n')
		output_file.write(content)

	def run(self):
		output_file = open(self.file_path, 'w')
		os.seteuid(0)
		conn = Connection(self.channel_number, self.group_id, 1)
		os.seteuid(self.euid)
		while self.running:
			try:
				msg = conn.recv()
				self.process_message(msg, output_file)
			except socket.timeout as e:
				pass
			except Exception as e:
				pass
		output_file.close()
		conn.close()

class PipeReceiver (threading.Thread):

	def __init__(self, pipe_name, file_path):
		threading.Thread.__init__(self)
		self.pipe_name = pipe_name
		self.file_path = file_path
		self.running = True
		
	def run(self):
		pipe = open(self.pipe_name, 'r')
		output = open(self.file_path, 'w')
		while self.running:
			size = pipe.read(4)
			if len(size) != 4:
				self.__shutdown(output, pipe)
				break
			bytes = struct.unpack('L', size)[0]
			content = pipe.read(bytes)
			if bytes == 4:
				unpacked_content = struct.unpack('L', content)[0]
				if (self.__is_number(unpacked_content) and 
					int(unpacked_content) == Constants.vmipl_msg_vm_end):
					self.__shutdown(output, pipe)
				else:
					output.write(content)
			else:
				output.write(content)

	def __shutdown(self, output, pipe):
		output.close()
		pipe.close()
		os.remove(self.pipe_name)
		self.running = False

	def __is_number(self, value):
		try:
			int(value)
			return True
		except ValueError:
			return False

class VmFinishedHandler (threading.Thread):

	def __init__(self, euid, channel_number, receivers, running_vms, 
															tmp_vm_file_path):
		threading.Thread.__init__(self)
		self.channel_number = channel_number
		self.receivers = receivers
		self.euid = euid
		self.running_vms = running_vms
		self.tmp_vm_file_path = tmp_vm_file_path
		self.running = True

	def run(self):
		os.seteuid(0)
		conn = Connection(self.channel_number, Connection.control_group_id, 1)
		os.seteuid(self.euid)
		while self.running:
			try:
				msg = conn.recv()
				if msg.type == Constants.vmipl_msg_vm_end:
					self.running = False
			except socket.timeout as e:
				pass
			except Exception as e:
				print e.__class__.__name__, e.message
		
		for receiver in self.receivers:
			receiver.running = False
		
		with Constants.vm_lock:
			self.running_vms.pop(self.channel_number, None)
		
		os.remove(self.tmp_vm_file_path)
			

			
