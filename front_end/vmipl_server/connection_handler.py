import os
import shutil
import time
import threading
import traceback

from vmipl.vmipl_parser import VmiplParser

from vmipl_aux.constants import Constants

from vmipl_communication.connection import Connection
from vmipl_communication.network_connection import NetworkConnection
from vmipl_communication.receiver import Receiver
from vmipl_communication.receiver import PipeReceiver
from vmipl_communication.receiver import VmFinishedHandler


class ConnectionHandler(threading.Thread):

	def __init__(self, socket, running_vms, qemu_path, pipes_directory):
		threading.Thread.__init__(self)
		self.conn = NetworkConnection(socket)
		self.running_vms = running_vms
		self.qemu_path = qemu_path
		self.pipes_directory = pipes_directory
	
	def run(self):
		if self.conn.received_start_command():
			self.__handle_start()
		else:
			print "reconfiguration not implemented yet"
			self.conn.close()
			
	def __handle_start(self):
		try:
			parser = VmiplParser()
			vm_file_path, vmipl_script = self.conn.get_start_parameters()
			parsed_script = parser.parse(vmipl_script)
			event_groups = parsed_script.initialize_probes()
			tmp_vm_file_path = vm_file_path + '_tmp'
			shutil.copyfile(vm_file_path, tmp_vm_file_path)
			self.create_vm(parsed_script, tmp_vm_file_path)
			
			server_response = self.build_server_response(parsed_script, 
																event_groups)
			self.conn.send_server_response(server_response)
			
			self.wait_for_open_connection(parsed_script.channel_number)
			receivers = self.setup_receivers(parsed_script.channel_number,
																event_groups)
			self.setup_stream_receivers(receivers, parsed_script.stream_probes)
			self.setup_finished_handler(parsed_script.channel_number, 
													receivers, tmp_vm_file_path)
			
		except Exception as e:
			traceback.print_exc()
			self.conn.send_server_response(e.message)
		finally:
			self.conn.close()
	
	def create_vm(self, script, vm_file_path):
		with Constants.vm_lock:
			self.obtain_channel_number(script)
			self.transfer_script(script)
			self.start_vm(script, vm_file_path)
	
	def obtain_channel_number(self, script):
		first_channel = Connection.first_nl_family
		for i in range(first_channel, Connection.last_nl_family + 1):
			if not i in self.running_vms:
				self.running_vms[i] = [script]
				script.channel_number = i
				break
		if script.channel_number == 0:
			raise TooManyVMsException()
			
	def transfer_script(self, script):
		conn = Connection(Constants.vmipl_channel)
		conn.send_script(script)
		conn.close()
		
	# this should be changed, since it is highly insecure and most likely 
	# unnecessary!!!
	def start_vm(self, script, vm_file_path):
		current_euid = os.geteuid()
		if os.path.isfile(vm_file_path):
			if script.stream_probes:
				tmp_path = self.add_stream_probe_configs(script.channel_number, 
											script.stream_probes, vm_file_path)
#			os.seteuid(0)
			os.system(self.qemu_path + " -readconfig " + vm_file_path + " &")
#			os.seteuid(current_euid)
		else:
			raise IOError("This is not a file: " + vm_file_path)
		
	def wait_for_open_connection(self, channel_number):
		connection_open = False
		count = 0
		while not connection_open and count < 10:
			time.sleep(1)
			try:
				connection = Connection(channel_number)
				connection_open = True
				connection.close()
			except:
				pass
		
	def add_stream_probe_configs(self, channel_number, 
												stream_probes, vm_file_path):
		for probe in stream_probes:
			probe.add_config(channel_number, vm_file_path, self.pipes_directory)
		
			
	def setup_receivers(self, channel_number, groups):
		receivers = []
		current_euid = os.geteuid()
	
		for output_channel in groups:
			if Receiver.is_file(output_channel):
				receiver = Receiver(channel_number, 
									groups[output_channel],
									output_channel, current_euid)
				receiver.start()
				receivers.append(receiver)
		
		return receivers		
	
	def setup_stream_receivers(self, receivers, stream_probes):
		for probe in stream_probes:
			if Receiver.is_file(probe.output_channel):
				receiver = PipeReceiver(probe.pipe_name, probe.output_channel)
				receiver.start()
				receivers.append(receiver)
		
	def setup_finished_handler(self, channel_number, receivers, 
															tmp_vm_file_path):
		current_euid = os.geteuid()
	
		finished_handler = VmFinishedHandler(current_euid, channel_number, 
											receivers, self.running_vms,
											tmp_vm_file_path)
		finished_handler.start()
		
		with Constants.vm_lock:
			self.running_vms[channel_number].append(finished_handler)
	
	def build_server_response(self, script, groups):
		vm_id = script.channel_number
		output_channels = {}
		output_pipes = {}
		response = ''
		
		response += 'VM ID: ' + str(vm_id) + '\n'
		
		if script.event_probes:
			response += '\nEvent Probe IDs:\n'
		
			for probe in script.event_probes:
				response += ('\t' + probe.get_name() + ': ' + 
									str(probe.probe_id) + '\n')
		
		if script.stream_probes:
			response += '\nStream Probe IDs:\n'
			
			for probe in script.stream_probes:
				response += ('\t' + probe.get_name() + ': ' + 
									str(probe.probe_id) + '\n')
		
		for output_channel in groups:
			if not Receiver.is_file(output_channel):
				output_channels[output_channel] = groups[output_channel]
				
		if len(output_channels) > 0:
			response += '\n'
			response += 'Output Channels:\n'
			
		for output_channel in output_channels:
			response += ('\t' + output_channel + ': ' + 
								str(output_channels[output_channel]) + '\n')
		
		for probe in script.stream_probes:
			if not Receiver.is_file(probe.output_channel):
				output_pipes[probe.output_channel] = probe.pipe_name
				
		if len(output_pipes) > 0:
			response += '\n'
			response += 'Output Pipes:\n'
			
		for output_pipe in output_pipes:
			response += ('\t' + output_pipe + ': ' + 
								str(output_pipes[output_pipe]) + '\n')
		
		return response
		
