# -*- coding: utf-8 -*-

# =========================================
# digitalsherlocks
# A DFRLab project
#
# Author: @estebanpdl
#
# File: Process collected arguments.
# =========================================


# Collect Arguments class
class CollectArguments(object):
	'''
	'''

	def _service_parser(self, service_request):
		'''
		Service parser
		'''
		opts = {
			'1': 'twitter'
		}

		return opts[service_request]

	def _get_subcommands(self, service):
		'''
		'''
		return {
			'foo': True
		}

	def _generate_args(self):
		'''

		Generates arguments based on inputs
		'''

		print ('')
		print ('')
		print ('Select service')

		'''
		Options
		'''
		print ('1. Twitter')

		
		# Get service
		print ('')
		service_request = ' '.join(input('> ').split()).strip()
		service = self._service_parser(service_request)
		args = {
			'service': service
		}

		'''

		Get subcommands
			- Retrieves inputs based on service
		'''
		subcommands = self._get_subcommands(service)
				
		return (lambda d: d.update(subcommands) or d)(args)


# Process Arguments class
class ProcessArguments(object):
	'''
	'''

	def __init__(self, args):
		'''
		'''

		if not args:
			args = CollectArguments()
			args = args._generate_args()

		self.args = args
		
	def get_parameters(self):
		'''
		'''
		return self.args
