from struct import *

from vmipl_aux.constants import Constants
from vmipl_aux.helper import Helper

class EventProbe ():

	def __init__(self, probe_type, probe_id, params):
		self.type = probe_type
		self.probe_id = probe_id
		self.data_probes = []
		self.filters = []
		self.pause = 0
		self.message_type = Constants.vmipl_msg_e_event

	def convert_to_struct(self):
		active_data_probes = Helper.get_active_value(self.data_probes)
		active_filters = Helper.get_active_value(self.filters)
		
		struct = pack('LPLHBBPPP',	self.type,
									0,
									self.probe_id,
									active_data_probes,
									active_filters,
									self.pause,
									0,
									0,
									0)
		return struct
		
	def get_name(self):
		return 'Event Probe'

class CRWrite (EventProbe):

	def __init__(self, probe_type, probe_id, params):
		EventProbe.__init__(self, probe_type, probe_id, params)
		self.cr_number = params[0]
		self.message_type = Constants.vmipl_msg_e_cr

	def convert_to_struct(self):
		active_data_probes = Helper.get_active_value(self.data_probes)
		active_filters = Helper.get_active_value(self.filters)
		
		struct = pack('LPLHBBPPPi', self.type,	
									0,
									self.probe_id,
									active_data_probes,
									active_filters,
									self.pause,
									0,
									0,
									0,
									int(self.cr_number))
		return struct
		
	def get_name(self):
		return 'CRWrite'

class AtEvent (EventProbe):

	def __init__(self, probe_type, probe_id, params):
		EventProbe.__init__(self, probe_type, probe_id, params)
		self.address = params[0]
		self.event_condition = 0
		self.dbg_register = 0
		self.message_type = Constants.vmipl_msg_e_event_at

	def convert_to_struct(self):
		active_data_probes = Helper.get_active_value(self.data_probes)
		active_filters = Helper.get_active_value(self.filters)
		
		struct = pack('LPLHBBPPPLBB', 	self.type,	
										0,
										self.probe_id,
										active_data_probes,
										active_filters,
										self.pause,
										0,
										0,
										0,
										int(self.address, 16),
										self.dbg_register,
										self.event_condition
										)
		return struct
		
	def get_name(self):
		name = 'Undefined AtEvent'
		if self.event_condition == Constants.vmipl_read:
			name = 'ReadAt'
		elif self.event_condition == Constants.vmipl_write:
			name = 'WriteAt'
		elif self.event_condition == Constants.vmipl_exec:
			name = 'ExecuteAt'
			
		return name
	
class Syscall (EventProbe):

	def __init__(self, probe_type, probe_id, params):
		EventProbe.__init__(self, probe_type, probe_id, params)
		self.number = '0' if len(params) == 0 else params[0]
		self.message_type = Constants.vmipl_msg_e_syscall
		
	def convert_to_struct(self):
		active_data_probes = Helper.get_active_value(self.data_probes)
		active_filters = Helper.get_active_value(self.filters)
		
		struct = pack('LPLHBBPPPi', 	self.type,	
										0,
										self.probe_id,
										active_data_probes,
										active_filters,
										self.pause,
										0,
										0,
										0,
										int(self.number)
										)
		return struct

	def get_name(self):
		return 'Syscall'

class OnExternalRequest (EventProbe):

	def __init__(self, probe_type, probe_id, params):
		EventProbe.__init__(self, probe_type, probe_id, params)
		self.request_id = params[0]
		self.message_type = Constants.vmipl_msg_e_ext_req
		
	def convert_to_struct(self):
		active_data_probes = Helper.get_active_value(self.data_probes)
		active_filters = Helper.get_active_value(self.filters)
		
		struct = pack('LPLHBBPPPi', 	self.type,	
										0,
										self.probe_id,
										active_data_probes,
										active_filters,
										self.pause,
										0,
										0,
										0,
										int(self.request_id)
										)
		
		return struct
