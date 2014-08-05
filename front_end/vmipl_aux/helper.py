

class Helper ():

	@staticmethod
	def get_active_value(elements):
		active = 0
		
		for element in elements:
			active |= element.type
			
		return active

	@staticmethod
	def get_active_dict_entries(dictionary, entries):
		active = 0
		for entry in entries:
			active |= dictionary[entry]
			
		return active
