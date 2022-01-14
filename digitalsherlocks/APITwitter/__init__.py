# -*- coding: utf-8 -*-

# =========================================
# digitalsherlocks
# A DFRLab project
#
# Author: @estebanpdl
#
# File: Twitter API requests.
# =========================================


# import modules
import sys
import time

from APITwitter.client import TwitterAuthentication
from twitter import TwitterHTTPError, TwitterError
from urllib.error import HTTPError

# import twitter utils
from APITwitter.utils import (
	clean_twitter_arguments, get_max_id
)

# import database
from APITwitter.database import Database


# API class
class API(object):
	'''
	'''

	def __init__(self, **kwargs):
		'''
		'''

		# Twitter API user connection
		self.TwitterAuth = TwitterAuthentication()
		self.TwitterAPI = self.TwitterAuth.connect()

		# Endpoint parameters
		self.kwargs = kwargs

		# Collected data
		self.data = None

		'''
		DB connection
		
		DB arguments
		'''
		db_args = {
			'db_path': kwargs['db_path'],
			'sql_file': kwargs['sql_file'],
			'update_existing_db': kwargs['update_existing_db']
		}
		self.db = Database()
		self.db_connection, self.db_cursor = self.db._connect_db(
			**db_args
		)

	def _insert_data(self):
		'''
		'''

		pass

	'''

	Build Twitter API endpoints
	'''
	def search_tweets(self):
		'''
		'''

		pass
		

	def user_timeline(self):
		'''

		Returns a collection of the most recent Tweets posted
		by the user indicated by the screen_name or user_id
		parameters.

		kwargs:
			- (screen_name | user_id)
			- since_id
			- count
			- max_id
			- exclude_replies
			- include_rts
		'''
		# Clean Twitter arguments
		self.kwargs = clean_twitter_arguments(self.kwargs)

		'''

		API request

		Endpoint: user_timeline
		'''
		self.data = []
		try:
			statuses = self.TwitterAPI.statuses.user_timeline(
				**self.kwargs
			)
			if len(statuses) > 0:
				self.data.extend(statuses)

				# Get max id
				max_id = get_max_id(statuses)

				# Download up to 3,200 user tweets
				while len(statuses) > 0:
					self.kwargs['max_id'] = max_id
					statuses = self.TwitterAPI.statuses.user_timeline(
						**self.kwargs
					)

					if len(statuses) > 0:
						self.data.extend(statuses)
						max_id = get_max_id(statuses)

		except (TwitterHTTPError, HTTPError, TwitterError) as e:
			error = e.__class__.__name__
			e_type, e_value, e_traceback = sys.exc_info()
			if error == 'TwitterError':

				# Retry < API request failed >
				print ('')
				print (error)
				print (f'E TYPE ---> {e_type}')
				print (f'E VALUE ---> {e_value}')
				print (f'E TRACEBACK ---> {e_traceback}')

			pass

		# Insert data to database
		return self.data, len(self.data)


	def user_connections(self, **kwargs):
		'''
		'''

		pass
