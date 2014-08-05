

class NotSupportedException (Exception):

	def __init__(self, value):
		self.value = value
	
	def __str__(self):
		return repr(self.value)

class TooManyAtEventsException (Exception):

	def __init__(self, value):
		self.value = value
	
	def __str__(self):
		return repr(self.value)
		
class TooManyOutputChannelsException (Exception):

	def __init__(self, value):
		self.value = value
	
	def __str__(self):
		return repr(self.value)
		
class TooManyVMsException (Exception):

	default_msg = 	("There are too many VMs running at the same time. " + 
					"All netlink channels are taken.")
					
	def __init__(self, value=default_msg):
		self.value = value
		
	def __str__(self):
		return repr(self.value)
