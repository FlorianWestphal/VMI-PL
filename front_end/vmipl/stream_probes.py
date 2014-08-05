import os

class StreamProbe:

	def __init__(self, probe_type, probe_id, output_channel, params):
		self.type = probe_type
		self.probe_id = probe_id
		self.output_channel = output_channel
		self.group_id = 0
		self.pipe_name = ''

	def add_config(self, file_path):
		pass
	
	def remove_pipe(self):
		if len(self.pipe_name) > 0:
			os.remove(self.pipe_name)
	
	def get_name(self):
		return 'Stream Probe'

class CaptureNetwork (StreamProbe):

	NO_VLAN_FOUND = -1

	def __init__(self, probe_type, probe_id, output_channel, params):
		StreamProbe.__init__(self, probe_type, probe_id, output_channel, params)
		self.mac = params[-1].replace(':', '')
		
	def add_config(self, channel_number, file_path, pipes_directory):
		self.pipe_name = '{0}/{1}_{2}_{3}'.format(pipes_directory, 'pipe', 
												channel_number, self.group_id)
		os.mkfifo(self.pipe_name)
	
		with open(file_path, 'r') as config_file:
			configs = self.__get_net_configs(config_file)

		vlan_id = None
		if not configs.has_key(CaptureNetwork.NO_VLAN_FOUND):
			for key in configs:
				for entry in configs[key]:
					if entry.startswith('macaddress'):
						mac = entry.split('=')[1].strip().replace('"', '')
						mac = mac.replace(':', '')
						if mac == self.mac:
							vlan_id = key
							break
				if vlan_id:
					break
			if not vlan_id:
				raise Exception("No network interface with mac: " + self.mac +
								" found")
		
		with open(file_path, 'a') as config_file:
			self.__append_configuration(config_file, vlan_id)								
	
	def __append_configuration(self, config_file, vlan_id):
		config_file.write('\n')
		config_file.write('[net]\n')
		config_file.write('  type = "dump"\n')
		config_file.write('  pipe_name = "' + self.pipe_name + '"\n')
		if vlan_id:
			config_file.write('  vlan = ' + str(vlan_id))
		
	def __get_net_configs(self, config_file):
		configs = {}
		config_buffer = []
		start_buffering = False
		
		for line in config_file:
			if line.startswith('[net]'):
				start_buffering = True
			elif len(line.strip()) == 0:
				start_buffering = False
				for entry in config_buffer:
					if entry.startswith('vlan'):
						key = entry.split('=')[1].strip()
						if configs.has_key(key):
							configs[key].extend(config_buffer)
						else:
							configs[key] = config_buffer
						config_buffer = []
			elif start_buffering:
				config_buffer.append(line.strip())

		if len(configs) == 0 and len(config_buffer) > 0:
			configs[CaptureNetwork.NO_VLAN_FOUND] = config_buffer
		elif len(configs) > 0 and len(config_buffer) > 0:
			raise Exception("Configuration file contains [net] entries with " +
								"and without vlan entries.""")
		elif len(configs) == 0 and len(config_buffer) == 0:
			raise Exception("No network device configured.")

		return configs
	
	def get_name(self):
		return 'CaptureNetwork'	
	
if __name__ == '__main__':
	print 'start program'
	probe = CaptureNetwork(0x1, 1, '#test', ['00:16:35:AF:94:4B'])
	probe.group_id = 2
	probe.add_config(23, '/home/florian/Desktop/test/ubuntu_12_04.cfg')
	print 'program finished'
