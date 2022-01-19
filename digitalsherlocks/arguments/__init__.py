# -*- coding: utf-8 -*-

# =========================================
# digitalsherlocks
# A DFRLab project
#
# Author: @estebanpdl
#
# File: Process collected arguments.
# =========================================

# import modules
import sys

# import from modules
from logs import log_time_fmt
from arguments.utils import (
	generate_wd, aligntext
)

# import APIs
from APITwitter import ApiTwitter

# Process Arguments class
class ProcessArguments(object):
	'''
	'''

	def __init__(self, args):
		'''
		'''

		if not args:

			print ('')
			print (f'{log_time_fmt()} - < ERROR >')
			print (f'{log_time_fmt()} - > No arguments were added')
			print (f'{log_time_fmt()} - > Check help parameter')
			print (f'{log_time_fmt()} - $ digitalsherlocks cli -h')

			# Future
			'''
			print (f'{log_time_fmt()} - User guided commands')

			args = CollectArguments()
			args = args._generate_args()

			'''

			# Exit program
			sys.exit()



		# Collect arguments
		self.args = args
		
	def _get_arguments(self):
		'''

		Returns arguments
		'''

		# Generate working directory
		update_database_status = self.args['update_database']
		if not update_database_status:
			'''

			Working directory will be used to store data.
			
			If an existing datatabase was added, as well as a new
			working directory, new data will be stored in wd, while
			updates will target the database.
			'''
			self.args['wd'] = generate_wd(self.args['wd'])

		print (f'{log_time_fmt()} - Arguments ready')
		return self.args

	def connect_service(self):
		'''
		'''
		# Get arguments
		kwargs = self._get_arguments()
		print (f'{log_time_fmt()} - Connecting to service')

		# Service
		service = kwargs['service']
		print (
			aligntext(
				f'{log_time_fmt()} - {service.capitalize()} service \
				connected'
			)
		)

		'''
		
		TEST API

		-> Twitter

		'''
		api_twitter = ApiTwitter(**kwargs)

		# users
		return api_twitter.user_timeline()
