from vmipl.vmipl_grammar import VmiPlGrammar
from vmipl.vmipl_types import Types
from vmipl.script import Script

from vmipl_aux.constants import Constants
from vmipl_aux.vmipl_exceptions import *

class VmiplParser ():

	def createDataProbeFrom(self, definition):
		probe_name = definition[0]
		types = Types.data_probe_types
		if probe_name not in types:
			raise NotSupportedException('"' + probe_name + '" not supported.')
		# create data probe
		probe = types[probe_name][1](types[probe_name][0], definition[-1],
															definition[1:-1])
		return probe

	def createFilterFrom(self, definition):
		filter_name = definition.filter_name[0]
		types = Types.filter_types
		if filter_name not in types:
			raise NotSupportedException('"' + filter_name + '" not supported.')
		# create filter
		new_filter = types[filter_name][1](types[filter_name][0], 
													definition.filter_name[1:])
		# add data probes
		for data_probe_definition in definition.data_probes:
			data_probe = self.createDataProbeFrom(data_probe_definition)
			new_filter.data_probes.append(data_probe)
			
		return new_filter

	def createEventProbeFrom(self, definition, probe_id):
		probe_name = definition.probe_name[0]
		types = Types.event_probe_types
		if probe_name not in types:
			raise NotSupportedException('"' + probe_name + '" not supported.')
		# create event probe
		probe = types[probe_name][1](types[probe_name][0], probe_id, 
													definition.probe_name[1:])
		if probe.type == Constants.vmipl_at_address:
			probe.event_condition = types[probe_name][2]
												
		# add filters
		for filter_definition in definition.filters:
			new_filter = self.createFilterFrom(filter_definition)
			probe.filters.append(new_filter)
	
		# add data probes
		for data_probe_definition in definition.data_probes:
			data_probe = self.createDataProbeFrom(data_probe_definition)
			probe.data_probes.append(data_probe)
	
		return probe

	def createStreamProbeFrom(self, definition, probe_id):
		probe_name = definition[0]
		types = Types.stream_probe_types
		if probe_name not in types:
			raise NotSupportedException('"' + probe_name + '" not supported.')
		# create stream probe
		probe = types[probe_name][1](types[probe_name][0], probe_id, 
										definition[-1], definition[1:-1])
										
		return probe

	def createScriptFrom(self, definition):
		probe_id = 0
		configurations = definition.configuration[1:]
		script = Script()
		for config in configurations:
			script.configuration[config[0]] = config[1]
		
		for event_probe_definition in definition.event_probes:
			event_probe = self.createEventProbeFrom(event_probe_definition, 
																	probe_id)
			script.event_probes.append(event_probe)
			probe_id += 1

		for stream_probe_definition in definition.stream_probes:
			stream_probe = self.createStreamProbeFrom(stream_probe_definition,
																	probe_id)
			script.stream_probes.append(stream_probe)
			probe_id += 1

		return script

	def parse(self, script):
		grammar = VmiPlGrammar()
		definition = grammar.parse(script)
		
		return self.createScriptFrom(definition)
		
