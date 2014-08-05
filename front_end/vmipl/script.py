from struct import *

from vmipl_aux.constants import Constants
from vmipl_aux.helper import Helper

from vmipl_communication.connection import Connection


class Script ():

	def __init__(self):
		self.configuration = 	{	'ProcessListHead':			'0',
									'TasksOffset':				'0',
									'PIDOffset':				'0',
									'ProcessNameOffset':		'0',
									'MMStructOffset':			'0',
									'ExeFileOffset':			'0',
									'DEntryOffset':				'0',
									'ParentOffset':				'0',
									'DNameOffset':				'0',
									'PGDOffset':				'0',
									'SyscallDispatcherAddress':	'0',
									'SyscallInterruptNumber':	'0',
									'SyscallNumberLocation':	'NULL'
								}
		self.event_probes = []
		self.stream_probes = []
		self.message_type = Constants.vmipl_msg_probes
		self.channel_number = 0

	def convert_to_struct(self):
		active_event_probes = Helper.get_active_value(self.event_probes)
	
		register = self.configuration['SyscallNumberLocation']
		syscall_location = Constants.readable_registers[register]
		interrupt_number = int(self.configuration['SyscallInterruptNumber'])
		
		struct = pack('BBPLLLLLLLLLLLLLBP', 	self.channel_number,
										active_event_probes,
										0,
										0,
										int(self.configuration['ProcessListHead'], 16),
										int(self.configuration['TasksOffset']),
										int(self.configuration['PIDOffset']),
										int(self.configuration['ProcessNameOffset']),
										int(self.configuration['MMStructOffset']),
										int(self.configuration['ExeFileOffset']),
										int(self.configuration['DEntryOffset']),
										int(self.configuration['ParentOffset']),
										int(self.configuration['DNameOffset']),
										int(self.configuration['PGDOffset']),
										int(self.configuration['SyscallDispatcherAddress'], 16),
										syscall_location,
										interrupt_number,
										0)
		return struct
	
	def initialize_probes(self):
		self.assign_dbg_registers()
		return self.assign_output_groups()
		
	def assign_dbg_registers(self):
		at_event_probes = filter(lambda x:x.type == Constants.vmipl_at_address, 
													self.event_probes)
	
		if len(at_event_probes) > 4:
			raise TooManyAtEventsException("Only four at events are allowed, " 
					" but "+ str(len(at_event_probes)) + "were configured.")
		else:
			dbg_registers = [Constants.vmipl_dbg_0, Constants.vmipl_dbg_1,
							Constants.vmipl_dbg_2, Constants.vmipl_dbg_3]
			for idx, at_event in enumerate(at_event_probes):
				at_event.dbg_register = dbg_registers[idx]
				
	def assign_output_groups(self):
		event_groups = {}
		stream_groups = {}
		group_id = Connection.min_group_id
	
		for event_probe in self.event_probes:
			group_id = self.assign_group_ids(event_probe.data_probes, 
														event_groups, group_id)
			for filter_item in event_probe.filters:
				group_id = self.assign_group_ids(filter_item.data_probes, 
													event_groups, group_id)
													
		self.assign_group_ids(self.stream_probes, stream_groups, group_id)
	
		if group_id > Connection.max_group_id:
			raise TooManyOutputChannelsException("It is only possible to " +
										"have 31 different output channels")
		return event_groups
		
	def assign_group_ids(self, probes, groups, group_id):
		for probe in probes:
			if probe.output_channel in groups:
				probe.group_id = groups[probe.output_channel]
			else:
				groups[probe.output_channel] = group_id
				probe.group_id = group_id
				group_id = group_id << 1
		return group_id
