from vmipl.event_probes import *
from vmipl.data_probes import *
from vmipl.stream_probes import *
from vmipl.filters import *

from vmipl_aux.constants import Constants


class Types ():

	event_probe_types 	= {	'CRWrite': 				[Constants.vmipl_cr_write, CRWrite],
							'OnResume': 			[Constants.vmipl_on_resume, EventProbe],
							'ReadAt': 				[Constants.vmipl_at_address, AtEvent, Constants.vmipl_read],
							'WriteAt': 				[Constants.vmipl_at_address, AtEvent, Constants.vmipl_write],
							'ExecuteAt': 			[Constants.vmipl_at_address, AtEvent, Constants.vmipl_exec],
							'OnExternalRequest':	[Constants.vmipl_external_request, OnExternalRequest],
							'Syscall':				[Constants.vmipl_syscall, Syscall]
						}
	
	data_probe_types 	= {	'ReadRegister': [1, ReadRegisterProbe],
							'ReadMemory': 	[2, ReadMemoryProbe],
							'ReadMemoryAt': [4, ReadMemoryAtProbe],
							'ProcessList': 	[8, ProcessListProbe]
						}
		
	stream_probe_types 	= { 'CaptureNetwork': [Constants.vmipl_net, CaptureNetwork]
						}
						
	filter_types 		= {	'RegisterHasValue':	[1, RegisterFilter],
							'ValueAtAddressIs':	[2, AddressFilter]
						}

