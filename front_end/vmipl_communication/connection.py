import socket
import struct
import os

from vmipl.event_probes import EventProbe

from vmipl_aux.constants import Constants


class Message:
	def __init__(self, msg_type, msglen, flags=0, seq=-1, payload=None):
		self.type = msg_type
		self.flags = flags
		self.seq = seq
		self.pid = -1
		self.payload = payload
		self.msglen = msglen

	def send(self, conn):
		if self.seq == -1:
			self.seq = conn.seq()

		self.pid = conn.pid
		length = len(self.payload)

		hdr = struct.pack("IHHII", length + 4 * 4, self.type,
								self.flags, self.seq, self.pid)
		conn.send(hdr + self.payload)


class Connection:

	# begin with second netlink group, since the first is used for 
	# exchanging control data between execution environment and kernel
	min_group_id = 1<<1
	max_group_id = 1<<31
	control_group_id = 1<<0
	
	first_nl_family = 23
	last_nl_family = 31

	def __init__(self, nltype, groups=0, timeout=None):
		self.descriptor = socket.socket(socket.AF_NETLINK, 
													socket.SOCK_RAW, nltype)
		self.descriptor.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)
		self.descriptor.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
		self.descriptor.bind((0, groups))
		self.descriptor.settimeout(timeout)
		self.pid, self.groups = self.descriptor.getsockname()
		self._seq = 0

	def send(self, msg):
		self.descriptor.send(msg)

	def seq(self):
		self._seq += 1
		return self._seq
	
	def recv(self, bufs=16384):
		contents, (nlpid, nlgrps) = self.descriptor.recvfrom(bufs)
		# XXX: python doesn't give us message flags, check
		#      len(contents) vs. msglen for TRUNC
		msglen, msg_type, flags, seq, pid = struct.unpack("IHHII",
				                                          contents[:16])
		msg = Message(msg_type, msglen, flags, seq, contents[16:])
		msg.pid = pid
		if msg.type == Constants.nlmsg_error:
			errno = -struct.unpack("i", msg.payload[:4])[0]
			if errno != 0:
				err = OSError("Netlink error: %s (%d)" % (
											        os.strerror(errno), errno))
				err.errno = errno
				raise err
		return msg
		
	def close(self):
		self.descriptor.close()
	
	def send_message(self, message_type, data, synchronous):
		msg = Message(message_type, 0, 0, -1, data)
		msg.send(self)
		del msg
		if synchronous:
			reply = self.recv()
			del reply
	
	def send_probes(self, probes):
		if len(probes) == 0:
			return
		mid = len(probes) / 2
		self.send_message(probes[mid].message_type, probes[mid].convert_to_struct(), True)
		if issubclass(probes[mid].__class__, EventProbe):
			self.send_probes(probes[mid].data_probes)
		self.send_probes(probes[:mid])
		self.send_probes(probes[mid+1:])
		
	
	def send_script(self, script):
		self.send_message(script.message_type, script.convert_to_struct(), True)
		
		sorted_probes = sorted(script.event_probes, key=lambda x: x.type)
		self.send_probes(sorted_probes)
		
		
		
