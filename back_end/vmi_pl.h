#ifndef VMI_PL_H
#define VMI_PL_H

#include <linux/kvm_host.h>
#include <linux/netlink.h>

#define VMI_PL_CHANNEL	22

/* message types */
#define VMI_PL_MSG_PROBES			1
#define VMI_PL_MSG_E_EVENT			2
#define VMI_PL_MSG_E_EVENT_AT		3
#define VMI_PL_MSG_E_CR				4
#define VMI_PL_MSG_E_SYSCALL		5
#define VMI_PL_MSG_E_EXT_REQ		6
#define VMI_PL_MSG_D_READ_REG		31
#define VMI_PL_MSG_D_READ_MEM		32
#define VMI_PL_MSG_D_READ_MEM_AT	33
#define VMI_PL_MSG_D_PROC_LIST		34
#define VMI_PL_MSG_D_PROC_LIST_END	35
#define VMI_PL_MSG_VM_END			65535

/* event probe types */
#define VMI_PL_CR_WRITE				0x01
#define VMI_PL_ON_RESUME			0x02
#define VMI_PL_AT_ADDRESS			0x04
#define VMI_PL_SYSCALL				0x08
#define VMI_PL_EXTERNAL_REQUEST		0x10

/* data probe types */
#define VMI_PL_READ_REG		0x1
#define VMI_PL_READ_MEM		0x2
#define VMI_PL_READ_MEM_AT	0x4
#define VMI_PL_PROC_LIST	0x8

/* filter types */
#define VMI_PL_REG_FILTER	0x1
#define VMI_PL_ADDR_FILTER	0x2

/* readable register IDs */
#define VMI_PL_EAX		0x1
#define VMI_PL_EBX		0x2
#define VMI_PL_ECX		0x4
#define VMI_PL_EDX		0x8
#define VMI_PL_ESI		0x10
#define VMI_PL_EDI		0x20
#define VMI_PL_ESP		0x40
#define VMI_PL_EBP		0x80
#define VMI_PL_EIP		0x100
#define VMI_PL_EFLAGS	0x200
#define VMI_PL_CR0		0x400
#define VMI_PL_CR2		0x800
#define VMI_PL_CR3		0x1000
#define VMI_PL_CR4		0x2000
#define VMI_PL_CS		0x4000
#define VMI_PL_SS		0x8000
#define VMI_PL_DS		0x10000
#define VMI_PL_ES		0x20000
#define VMI_PL_FS		0x40000
#define VMI_PL_GS		0x80000
#define VMI_PL_TR		0x100000
#define VMI_PL_LDTR		0x200000
#define VMI_PL_GDTR		0x400000
#define VMI_PL_IDTR		0x800000

/* readable register size groups */
#define VMI_PL_REGISTERS	0x003fff
#define VMI_PL_SEGMENTS		0x3fc000
#define VMI_PL_DTABLES		0xc00000

/* readable registers number */
#define VMI_PL_REGISTERS_COUNT	24

/* at event conditions */
#define VMI_PL_READ		1
#define VMI_PL_WRITE	2
#define VMI_PL_EXEC		3

/* at event debug registers */
#define VMI_PL_DBG_0	0
#define VMI_PL_DBG_1	1
#define VMI_PL_DBG_2	2
#define VMI_PL_DBG_3	3
#define VMI_PL_DBG_7	7

#define VMI_PL_DBG_0_SET	0x1
#define VMI_PL_DBG_1_SET	0x2
#define VMI_PL_DBG_2_SET	0x4
#define VMI_PL_DBG_3_SET	0x8

/* process list fields */
#define VMI_PL_PROC_PID		0x1
#define VMI_PL_PROC_NAME	0x2
#define VMI_PL_PROC_PGD		0x4
#define VMI_PL_PROC_PATH	0x8

/* debug register configuration */
#define VMI_PL_DBG_0_GLOBAL		0x2
#define VMI_PL_DBG_1_GLOBAL		0x8
#define VMI_PL_DBG_2_GLOBAL		0x20
#define VMI_PL_DBG_3_GLOBAL		0x80
#define VMI_PL_DBG_0_ON_WRITE	0x10000
#define VMI_PL_DBG_1_ON_WRITE	0x100000
#define VMI_PL_DBG_2_ON_WRITE	0x1000000
#define VMI_PL_DBG_3_ON_WRITE	0x10000000
#define VMI_PL_DBG_0_ON_ACCESS	0x20000
#define VMI_PL_DBG_1_ON_ACCESS	0x200000
#define VMI_PL_DBG_2_ON_ACCESS	0x2000000
#define VMI_PL_DBG_3_ON_ACCESS	0x2000000

/* processor flags */
#define VMI_PL_DF		0x1000000000

/* tree struct definition */

struct vmipl_tree {
	__u32 type;
	struct vmipl_tree *left, *right;
	void *value;
};

/* vcpu list struct definition */
struct vmipl_vcpu_list {
	struct kvm_vcpu *vcpu;
	struct vmipl_vcpu_list *next;
	unsigned char protocol_type;
};


/* event data probe struct definitions */

struct vmipl_data_struct {
	struct vmipl_data_struct *next;		// important for the tree handling that next pointer is in first place of the struct
	__u32 group_id;
};

struct vmipl_read_reg_struct {
	struct vmipl_data_struct data_struct;
	__u32 registers;
};

struct vmipl_read_mem_struct {
	struct vmipl_data_struct data_struct;
	unsigned long address;
	unsigned long size;
};

struct vmipl_proc_list_struct {
	struct vmipl_data_struct data_struct;
	__u8 fields;
};

struct vmipl_read_mem_at_struct {
	struct vmipl_data_struct data_struct;
	__u32 selected_register;
	unsigned long size;
	unsigned long offset;
};

/* filter struct definitions */

struct vmipl_address_filter {
	unsigned long virtual_address;
	unsigned long value;
	unsigned char pause;
	__u16 active_data_probes;
	struct vmipl_tree *data_probes_root;
	struct vmipl_address_filter *next;
};

struct vmipl_register_filter {
	__u32 selected_register;
	unsigned long value;
	unsigned char pause;
	__u16 active_data_probes;
	struct vmipl_tree *data_probes_root;
	struct vmipl_register_filter *next;
};

/* event probe struct definitions */

struct vmipl_event_struct {
	struct vmipl_event_struct *next;	// important for the tree handling that next pointer is in first place of the struct
	__u32 probe_id;
	__u16 active_data_probes;
	__u8 active_filters;
	unsigned char pause;
	struct vmipl_tree *data_probes_root;
	struct vmipl_address_filter *address_filters;
	struct vmipl_register_filter *register_filters;
};

struct vmipl_cr_event_struct {
	struct vmipl_event_struct event_probe_definitions;
	int cr;
};

struct vmipl_at_event_struct {
	struct vmipl_event_struct event_probe_definitions;
	unsigned long address;
	unsigned char dbg_register;
	unsigned char event_condition;
};

struct vmipl_syscall_struct {
	struct vmipl_event_struct event_probe_definitions;
	int syscall_nr;
};

struct vmipl_external_request_struct {
	struct vmipl_event_struct event_probe_definitions;
	int request_id;
};

struct vmipl_os_settings{
	unsigned long proc_list_address;
	unsigned long tasks_offset;
	unsigned long pid_offset;
	unsigned long proc_name_offset;
	unsigned long mm_struct_offset;
	unsigned long exe_file_offset;
	unsigned long dentry_offset;
	unsigned long parent_offset;
	unsigned long dname_offset;
	unsigned long pgd_offset;
	unsigned long syscall_dispatch_address;
	__u32 syscall_nr_location;
	unsigned char syscall_interrupt_nr;
};

/* vmi-pl probe struct definition */

struct vmipl_probe_struct {
	unsigned char channel_nr;
	unsigned char active_event_probes;
	struct sock *nl_socket;
	unsigned long received_requests;
	struct vmipl_os_settings os_settings;
	
	struct vmipl_tree *event_root;
	
};


/* output structs */

struct vmipl_segment {
	unsigned long base;
	__u32 limit;
	__u16 selector;
	__u8  type;
	__u8  present, dpl, db, s, l, g, avl;
};

struct vmipl_dt {
	__u64 base;
	__u16 limit;
};


/* helper structs */
struct vmipl_connect_info {
	struct sk_buff *skb;
	struct nlmsghdr *nlh;
	struct sock *nl_socket;
	sk_buff_data_t tmp;
};


/* netlink message handler */
void vmipl_data_ready(struct sk_buff *skb);
void vmipl_vcpu_netlink_handler(struct sk_buff *skb);
struct vmipl_event_struct* vmipl_create_event(void *msg, unsigned long size, __u32 probe_type);
void vmipl_create_data_probe(void *msg, unsigned long size, __u32 probe_type);


/* event probe handlers */
void vmipl_handle_cr_write(struct kvm_vcpu *vcpu, int cr);
void vmipl_handle_on_resume(struct kvm_vcpu *vcpu);
void vmipl_handle_db(struct kvm_vcpu *vcpu, unsigned long dr6);
void vmipl_handle_syscall(struct kvm_vcpu *vcpu, unsigned char syscall_nr); 
void vmipl_handle_on_external_request(struct kvm_vcpu *vcpu);


/* data probe handlers */
void vmipl_read_register_probe(struct kvm_vcpu *vcpu, struct vmipl_read_reg_struct *read_register, __u32 event_probe_id);
void vmipl_read_memory_probe(struct kvm_vcpu *vcpu, struct vmipl_read_mem_struct *read_memory, __u32 event_probe_id);
void vmipl_read_memory_at_probe(struct kvm_vcpu *vcpu, struct vmipl_read_mem_at_struct *read_memory_at, __u32 event_probe_id);
void vmipl_process_list_probe(struct kvm_vcpu *vcpu, struct vmipl_proc_list_struct *process_list, __u32 event_probe_id); 


/* helper functions */
void vmipl_prepare_sending(struct vmipl_connect_info *connect_info, unsigned long size);
void vmipl_send(struct vmipl_connect_info *connect_info, unsigned char group_id, __u16 msg_type);

unsigned long vmipl_register_data_size(__u32 registers);
unsigned int vmipl_number_of_set_bits(__u32 i);

unsigned char vmipl_process_filters(struct kvm_vcpu *vcpu, struct vmipl_event_struct *event);
void vmipl_process_data_probes(struct kvm_vcpu *vcpu, __u32 event_probe_id, __u16 active_data_probes, struct vmipl_tree *root);

unsigned long vmipl_read_selected_register(struct kvm_vcpu *vcpu, __u32 selected_register);
void vmipl_read_segment(struct kvm_vcpu *vcpu, struct vmipl_segment *segment, __u32 selected_segment);
void vmipl_read_dt(struct kvm_vcpu *vcpu, struct vmipl_dt *dt, __u32 selected_dt);
void vmipl_read_memory(struct kvm_vcpu *vcpu, unsigned long va, void *buffer, int buffer_size);
void* vmipl_read_string_from_memory(struct kvm_vcpu *vcpu, unsigned long va, int* size);
void* vmipl_read_linux_path(struct kvm_vcpu *vcpu, unsigned long mm_address, unsigned int* path_length);

void vmipl_write_to_address(struct kvm_vcpu *vcpu, unsigned long va, void *data, int data_size);

void vmipl_set_dr7(struct vmipl_at_event_struct *at_event, unsigned long *dr7_content);

void vmipl_emulate_instructions(struct kvm_vcpu *vcpu);

/* functions for tree handling */
void vmipl_tree_insert(struct vmipl_tree **root, void *value, __u32 probe_type);
void* vmipl_get_tree_element(struct vmipl_tree *root, __u32 type);
void vmipl_free_event_tree(struct vmipl_tree *root);
void vmipl_free_data_probe_tree(struct vmipl_tree *root);
void vmipl_free_linked_list(char **next);

/* functions for vcpu list handling */
void vmipl_vcpu_list_add(struct vmipl_vcpu_list **list, struct kvm_vcpu *vcpu, unsigned char protocol_type);
struct kvm_vcpu* vmipl_vcpu_list_get(struct vmipl_vcpu_list *list, unsigned char protocol_type);
unsigned char vmipl_vcpu_list_remove(struct vmipl_vcpu_list **list, struct kvm_vcpu *vcpu);
#endif	//VMI_PL_H
