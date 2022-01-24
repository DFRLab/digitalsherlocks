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
import os
import sys

# import from modules
from logs import printl
from arguments.utils import (
	generate_wd
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
			printl('< ERROR >', color='RED')
			printl('> No arguments were added', color='RED')
			printl('> Check help parameter', color='RED')
			printl('$ digitalsherlocks cli -h', color='GREEN')

			# Future
			'''
			printl('User guided commands', color='BLUE')

			args = CollectArguments()
			args = args._generate_args()

			'''

			# Exit program
			sys.exit()



		# Collect arguments
		self.args = args
		
	def _get_wd(self):
		'''
		'''
		wd = os.path.abspath(self.args['wd'])
		return wd.replace(os.sep, '/')

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
		else:
			dbpath = self.args['dbpath']
			self.args['wd'] = os.path.dirname(dbpath) \
				if self.args['wd'] == None else self.args['wd']

		printl('Arguments ready')

		'''
		Working directory
		'''
		wd = self._get_wd()
		printl(f'Working directory: {wd}', color='GREEN')

		return self.args

	def connect_service(self):
		'''
		'''
		# Get arguments
		kwargs = self._get_arguments()
		printl('Connecting to service')

		# Service
		service = kwargs['service']
		printl(f'{service.capitalize()} service connected')

		'''
		
		TMP API

		-> Twitter
		-> TODO: Improve

		'''
		api_twitter = ApiTwitter(**kwargs)

		# Service < tmp process >
		if service == 'twitter' and kwargs['update_db_attrs']:
			api_twitter._update_database_using_attrs()
		else:
			if service == 'twitter':
				endpoint = kwargs['endpoint']

				if endpoint == 'users':
					api_twitter.user_timeline()

				if endpoint == 'tweets':
					api_twitter.search_tweets()

				if endpoint == 'friendships':
					api_twitter.friendships()
