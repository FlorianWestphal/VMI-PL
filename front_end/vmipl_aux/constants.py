import threading


class Constants ():

	vm_lock = threading.Lock()

	vmipl_channel			= 22

	nlmsg_error				= 2

	# message types
	vmipl_msg_probes			= 1
	vmipl_msg_e_event			= 2
	vmipl_msg_e_event_at		= 3
	vmipl_msg_e_cr				= 4
	vmipl_msg_e_syscall			= 5
	vmipl_msg_e_ext_req			= 6
	vmipl_msg_e_net				= 7
	vmipl_msg_d_read_reg		= 31
	vmipl_msg_d_read_mem		= 32
	vmipl_msg_d_read_mem_at		= 33
	vmipl_msg_d_proc_list		= 34
	vmipl_msg_d_proc_list_end	= 35
	vmipl_msg_vm_end			= 65535

	# event probe types
	vmipl_cr_write 			= 0x1
	vmipl_on_resume			= 0x2
	vmipl_at_address		= 0x4
	vmipl_syscall			= 0x8
	vmipl_external_request 	= 0x10
	
	# stream probe types
	vmipl_net				= 0x1
	
	# at event conditions
	vmipl_read			= 0x1
	vmipl_write			= 0x2
	vmipl_exec			= 0x3
	
	# at event debug registers
	vmipl_dbg_0			= 0
	vmipl_dbg_1			= 1
	vmipl_dbg_2			= 2
	vmipl_dbg_3			= 3
	vmipl_dbg_7			= 7
	
	# process list fields
	vmipl_pid			= 0x1
	vmipl_name			= 0x2
	vmipl_pgdp			= 0x4
	vmipl_path			= 0x8
	
	readable_registers = {	'NULL':		0,
							'EAX':		1,
							'EBX':		2,
							'ECX':		4,
							'EDX':		8,
							'ESI':		16,
							'EDI':		32,
							'ESP':		64,
							'EBP':		128,
							'EIP':		256,
							'EFLAGS':	512,
							'CR0':		1024,
							'CR2':		2048,
							'CR3':		4096,
							'CR4':		8192,
							'CS':		16384,
							'SS':		32768,
							'DS':		65536,
							'ES':		131072,
							'FS':		262144,
							'GS':		524288,
							'TR':		1048576,
							'LDTR':		2097152,
							'GDTR':		4194304,
							'IDTR':		8388608
							}
							
	process_list_fields = 	{	'PID':		vmipl_pid,
								'NAME':		vmipl_name,
								'PGDP':		vmipl_pgdp,
								'PATH':		vmipl_path
							}
