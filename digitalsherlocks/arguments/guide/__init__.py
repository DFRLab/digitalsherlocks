# -*- coding: utf-8 -*-

# =========================================
# digitalsherlocks
# A DFRLab project
#
# Author: @estebanpdl
#
# File: Collected arguments from user
# =========================================

# import modules
import sys
import time

# Collect Arguments class
class CollectArguments(object):
	'''
	'''

	def _service_parser(self, service_request):
		'''

		Service parser
		'''
		service_request = aligntext(service_request)
		opts = {
			'1': 'twitter'
		}

		return opts[service_request]

	def _get_service(self):
		'''
		'''

		print ('')
		print ('')
		print ('Select service')
		print ('==============')
		print ('')

		'''
		Service options
		'''
		print ('1. Twitter')

		# Get service
		print ('')
		service_request = input('> Option: ')
		service = self._service_parser(service_request)

		return {
			'service': service
		}

	def _twitter_endpoint_parser(self, endpoint_request):
		'''

		endpoint parser for Twitter API options
		'''
		endpoint_request = aligntext(endpoint_request)
		opts = {
			'1': 'users',
			'2': 'tweets'
		}

		return opts[endpoint_request]

	def _twitter_endpoint_options(self):
		'''
		'''
		print ('')
		print ('')
		print ('Twitter API options')
		print ('===================')
		print ('')

		# Options
		print ('1. A user timeline')
		print ('2. Search tweets by hashtag or keywords')

		# Get endpoint
		print ('')
		gpo = input('> Option: ')

		return gpo

	def _handle_twitter_boolean_params(self, key, value):
		'''
		'''
		boolean_args = [
			'exclude_replies', 'include_rts'
		]
		
		if key in boolean_args:
			try:
				value = bool(int(value))
			except ValueError:
				print ('')
				print ('')
				print ('''

				=======================================
					
				  Boolean arguments should be 1 or 0.
				  Try again

				=======================================
				''')
				print ('')
				print ('')

				# Exit program
				sys.exit()

		return value

	def _get_twitter_commands(self, endpoint):
		'''

		Gets twitter commands < arguments > by endpoint
		'''

		args = {
			'users': {
				'screen_name': '''
					> Username
					
					<
						Do not INCLUDE @ |
						Keep empty if you will add a user id instead
					>
				''',
				'user_id': '''
					> User ID

					<
						Keep empty if username was added
					>
				''',
				'exclude_replies': '''
					> Exclude Replies: 0. [False], 1. [True]
					
					<
						Values should be 0 or 1
					>
				''',
				'include_rts': '''
					> Include Retweets: 0. [False], 1. [True]
					
					<
						Values should be 0 or 1
					>
				'''
			},
			'tweets': {
				'q': '> Query: '
			}
		}

		action = args[endpoint].copy()

		'''

		Log type of action
		'''
		type_of_action = aligntext(
			f'''
				Select API parameters for the Twitter option: {
					endpoint.capitalize()
				}
			'''
		)
		
		print ('')
		print ('')
		print (type_of_action)
		print ('=' * len(type_of_action))
		print ('')

		# Focus
		time.sleep(5)

		# Iterate action based on endpoint
		for k, v in action.items():
			action[k] = aligntext(
				input(
					f'{aligntext(v)}: '
				)
			)
			if not action[k]:
				action[k] = None

			# handle twitter boolean parameters
			action[k] = self._handle_twitter_boolean_params(
				k, action[k]
			)

		'''

		Return exception if both screen_name and user_id have values
		'''

		return action

	def _twitter_database_args(self):
		'''
		'''
		db_args = {
			'update_database': '''
			Do you want to update a database? 0. [False], 1. [True]

			<
				Values should be 0 or 1
			>
			''',
			'dbpath': '''Add the path from the database that you
			want to update:
			''',
			'dbname': 'Add a custom database name, if needed:'
		}

		tmp_args = {}
		pass

	def _get_subcommands(self, service):
		'''
		'''
		tree = {
			'twitter': {
				'endpoint': self._twitter_endpoint_parser(
					self._twitter_endpoint_options()
				)
			}
		}

		commands = {
			'twitter': self._get_twitter_commands(
				tree[service]['endpoint']
			)
		}

		# Get custom service argument (i.e. endpoint for Twitter)
		args = tree[service]

		# Updating commands and custom service argument
		return (lambda d: d.update(commands[service]) or d)(args)

	def _generate_args(self):
		'''

		Generates arguments based on inputs
		'''

		# Digitalsherlocks will collect arguments based on inputs
		print ('')
		print ('')
		print ('> Collecting arguments')
		print ('______________________')

		# Intructions
		print ('')
		print ('')
		print ('==================================================')
		print ('#                                                #')
		print ('# Follow the next parameters.                    #')
		print ('# For multiple choice arguments: .               #')
		print ('#     Select the numeric option: [1, 2, 3, etc]  #')
		print ('#                                                #')
		print ('==================================================')
		print ('')

		# Focus
		time.sleep(5)

		# Get service
		args = self._get_service()
		service = args['service']

		'''

		Get subcommands
			- Retrieves inputs based on service
		'''
		subcommands = self._get_subcommands(service)
				
		return (lambda d: d.update(subcommands) or d)(args)
