from pyparsing import *

class VmiPlGrammar ():

	ParserElement.setDefaultWhitespaceChars(" ")

	@staticmethod
	def parse(input_string):
		tab = Suppress('\t')
		newline = Suppress('\n')
		ob = Suppress('(')
		cb = Suppress(')')
		ocb = Suppress('{')
		ccb = Suppress('}')
		comma = Suppress(',')
		colon = Suppress(':')
		hash_symbol = '#'
		hex_indicator = Suppress('0x')
		va = hex_indicator + Word(hexnums, exact=8)
		hex_value = hex_indicator + Word(hexnums)
		number = Word(nums)
		size = number
		offset = number
		mac_address = Word(alphanums + ':')
		filepath = Word(alphanums + '/' + '_')
		stream_id = Combine(hash_symbol + Word(alphanums))
		readable_register = oneOf('''EAX EBX ECX EDX ESI EDI ESP EBP EFLAGS CS SS DS 
									ES FS GS TR LDTR GDTR IDTR CR0 CR2 CR3 CR4''')
		vmcs_field = oneOf('''VIRTUAL_PROCESSOR_ID VM_EXIT_REASON  VM_EXIT_INTR_INFO 
								VM_EXIT_INTR_ERROR_CODE IDT_VECTORING_INFO_FIELD 
								IDT_VECTORING_ERROR_CODE EXIT_QUALIFICATION''')
		proc_field = oneOf('''PID NAME PATH PGDP''')
	
		config_item = (tab + Group('ProcessListHead' + colon + va |
								'TasksOffset' + colon + number |
								'PIDOffset' + colon + number |
								'ProcessNameOffset' + colon + number |
								'MMStructOffset' + colon + number |
								'ExeFileOffset' + colon + number |
								'DEntryOffset' + colon + number |
								'ParentOffset' + colon + number |
								'DNameOffset' + colon + number |
								'PGDOffset' + colon + number |
								'SyscallDispatcherAddress' + colon + va |
								'SyscallInterruptNumber' + colon + number |
								'SyscallNumberLocation' + colon + readable_register) 
							+ newline)
		configuration = Group(Group('Configuration') + ocb + newline +
						OneOrMore(config_item) + ccb
						+ newline).setResultsName('configuration')
	
		vmcs_field_item = comma + vmcs_field
		vmcs_fields = vmcs_field + ZeroOrMore(vmcs_field_item)
		proc_field_item = comma + proc_field
		proc_fields	= proc_field + ZeroOrMore(proc_field_item)
	
		data_probe_name = tab + ("ReadRegister" + ob + readable_register + comma |
							"ReadMemory" + ob + va + comma +  size + comma |
							"ReadMemoryAt" + ob + readable_register + comma 
							+ size + comma + offset + comma |
							"ReadVMCS" + ob + vmcs_fields + comma |
							"ProcessList" + ob + proc_fields + comma)
		probe_output = (stream_id | filepath)
		data_probe = Group(	data_probe_name 
							+ probe_output + cb
							+ newline)
		filter_data_probe = tab + data_probe
	
		filter_name = Group("RegisterHasValue" + ob + readable_register + comma
								+ hex_value + cb |
							"ValueAtAddressIs" + ob + va + comma + hex_value 
								+ cb).setResultsName('filter_name')
		filter_block = (ocb + newline 
							+ OneOrMore(filter_data_probe).setResultsName('data_probes') 
							+ tab + ccb)
		filters = Group(tab + filter_name + filter_block + newline)
	
		evt_probe_name = Group("CRWrite" + ob + number + cb |
							"IDTRWrite" |
							"GDTRWrite" |
							"IDTWrite" |
							"GDTWrite" |
							"MSRWrite" |
							"OnResume" |
							"ReadAt" + ob + va + cb |
							"WriteAt" + ob + va + cb |
							"ExecuteAt" + ob + va + cb |
							"OnExternalRequest" + ob + number + cb |
							"Syscall" + Optional(ob + number + cb)).setResultsName('probe_name')
		evt_probe_block = (ocb + newline
							+ ZeroOrMore(filters).setResultsName('filters') 
							+ ZeroOrMore(data_probe).setResultsName('data_probes')
							+ ccb)
		event_probe = Group(evt_probe_name + evt_probe_block) + newline
					
		str_probe_name = ("CaptureNetwork" + ob + mac_address + comma |
								"CaptureKeyboardInput" + ob)
		stream_probe = Group(str_probe_name + probe_output + cb + newline)
	
		probes = (ZeroOrMore(event_probe).setResultsName('event_probes')
					+ ZeroOrMore(stream_probe).setResultsName('stream_probes'))
	
		script = ZeroOrMore(configuration) + probes
		script.parseWithTabs()
		return script.parseString(input_string)
