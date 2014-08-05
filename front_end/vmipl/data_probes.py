from struct import *

from vmipl_aux.constants import Constants
from vmipl_aux.helper import Helper

class DataProbe ():

	def __init__(self, probe_type, output_channel):
		self.type = probe_type
		self.output_channel = output_channel
		self.group_id = 0


class ReadRegisterProbe (DataProbe):

	def __init__(self, probe_type, output_channel, params):
		DataProbe.__init__(self, probe_type, output_channel)
		self.register = params[0]
		self.message_type = Constants.vmipl_msg_d_read_reg

	def convert_to_struct(self):
		register = Constants.readable_registers[self.register]
		
		struct = pack('LPLL', 	self.type,
								0,
								self.group_id,
								register
								)
		return struct

class ReadMemoryProbe (DataProbe):

	def __init__(self, probe_type, output_channel, params):
		DataProbe.__init__(self, probe_type, output_channel)
		self.va = params[0]
		self.size = params[1]
		self.message_type = Constants.vmipl_msg_d_read_mem

	def convert_to_struct(self):
		
		struct = pack('LPLLL', 	self.type,
								0,
								self.group_id,
								int(self.va, 16),
								int(self.size)
								)
		
		return struct

class ReadMemoryAtProbe (DataProbe):

	def __init__(self, probe_type, output_channel, params):
		DataProbe.__init__(self, probe_type, output_channel)
		self.register = params[0]
		self.size = params[1]
		self.offset = params[2]
		self.message_type = Constants.vmipl_msg_d_read_mem_at

	def convert_to_struct(self):
		register = Constants.readable_registers[self.register]
		
		struct = pack('LPLLLL', self.type,
								0,
								self.group_id,
								register,
								int(self.size),
								int(self.offset)
								)
		
		return struct

class ProcessListProbe (DataProbe):

	def __init__(self, probe_type, output_channel, params):
		DataProbe.__init__(self, probe_type, output_channel)
		self.proc_fields = params
		self.message_type = Constants.vmipl_msg_d_proc_list

	def convert_to_struct(self):
		fields = Helper.get_active_dict_entries(Constants.process_list_fields, 
												self.proc_fields)

		struct = pack('LPLB', 	self.type,
									0,
									self.group_id,
									fields
									)
		
		return struct

