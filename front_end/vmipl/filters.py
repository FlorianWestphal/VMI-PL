from struct import *

from vmipl_aux.constants import Constants
from vmipl_aux.helper import Helper

class Filter ():

	def __init__(self, filter_type):
		self.type = filter_type
		self.data_probes = []
		self.pause = 0


class RegisterFilter (Filter):

	def __init__(self, filter_type, params):
		Filter.__init__(self, filter_type)
		self.register = params[0]
		self.value = params[1]

	def convert_to_struct(self):
		active_data_probes = Helper.get_active_value(self.data_probes)
		register = Constants.readable_registers[self.register]
		
		struct = pack('LLBHPP',	register,
								int(self.value),
								self.pause,
								active_data_probes,
								0,
								0)
		return struct

class AddressFilter (Filter):

	def __init__(self, filter_type, params):
		Filter.__init__(self, filter_type)
		self.va = params[0]
		self.value = params[1]

	def convert_to_struct(self):
		active_data_probes = Helper.get_active_value(self.data_probes)
		
		struct = pack('LLBHPP',	int(self.va, 16),
								int(self.value),
								self.pause,
								active_data_probes,
								0,
								0)
		return struct
