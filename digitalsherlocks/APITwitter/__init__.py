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
import logging


from APITwitter.client import TwitterAuthentication
from twitter import TwitterHTTPError, TwitterError
from urllib.error import HTTPError

# import twitter utils
from APITwitter.utils import (
	clean_twitter_arguments, get_max_id
)

# import database
from APITwitter.database import Database

'''

import storage <tmp code>

TODO: Storage class.
'''
from APITwitter.storage import insert_data


# API class
class API(object):
	'''
	'''

	def __init__(self, **kwargs):
		'''
		'''

		# Get main arguments
		self.kwargs = kwargs

		# Twitter API user connection
		logging.info('Twitter user authentication.')
		self.TwitterAuth = TwitterAuthentication()
		self.TwitterAPI = self.TwitterAuth.connect()

		# Get working directory
		self.wd = self.kwargs['wd']

		# Requested attrs
		self.timezone = self.kwargs['timezone']

		# Get database-related arguments
		self.update_database = self.kwargs['update_database']
		self.dbpath = self.kwargs['dbpath']
		self.dbname = self.kwargs['dbname']

		# Get DB connection
		self.db_connection = None
		self.db_cursor = None

		# Twitter endpoints
		self.endpoint = self.kwargs['endpoint']

		# Collected data
		self.data = None

	def _get_db_conn(self):
		'''

		Connects to sqlite database
		'''
		# Build database arguments
		db_args = {
			'wd': self.wd,
			'update_database': self.update_database,
			'dbpath': self.dbpath,
			'dbname': self.dbname,
			'endpoint': self.endpoint
		}

		# Database instance
		self.db = Database(**db_args)
		return self.db._connect_db()


	def _insert_data(self):
		'''

		Inserts data into database.

		- Function checks first if there is a database connection.
		'''
		if self.db_connection == None:
			self.db_connection, self.db_cursor = self._get_db_conn()

		# Insert data
		insert_data(
			self.db_connection,
			self.db_cursor,
			self.data,
			self.timezone
		)

	def _endpoint_status_parser(self, endpoint_status):
		'''

		Returns rate limit status' key (i.e. statuses, friends, etc.)
		'''

		src = {
			'/statuses/user_timeline': 'statuses'
		}

		return src[endpoint_status]

	def _rate_limit_status(self, endpoint_status):
		'''

		Checks rate limits
		'''
		status = self.TwitterAPI.application.rate_limit_status()
		resource = status['resources']['statuses'][endpoint_status]

		# Resources
		remaining = resource['remaining']
		reset = resource['reset']

		return remaining, reset

	def _sleep_application(self, endpoint_status):
		'''

		Sleeps application if rate limit status is low
		'''
		remaining, reset = self._rate_limit_status(endpoint_status)
		if remaining <= 10:
			sleep_for = int(reset - time.time()) + 10

			# Log action
			logging.warning('Application reached rate limits.')
			logging.info(
				f'Sleeping application for {sleep_for} secs...'
			)

			# Sleep application
			time.sleep(sleep_for)

			# Awake
			logging.info('Awake.')

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

		LOGS
		'''
		try:
			u = self.kwargs['screen_name']
		except KeyError:
			u = self.kwargs['user_id']

		logging.info(f'Downloading timeline from user {u}')

		'''

		Check rate limits
		'''
		endpoint_status = '/statuses/user_timeline'
		self._sleep_application(endpoint_status)

		'''

		API request

		Endpoint: user_timeline
		'''
		while True:
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

					break

			except (TwitterHTTPError, HTTPError, TwitterError) as e:
				error = e.__class__.__name__
				e_type, e_value, e_traceback = sys.exc_info()
				if error == 'TwitterError':

					# Retry < API request failed >
					if 'Incomplete JSON data collected' in e_value:
						logging.error(
							'Twitter Error connection. Retrying...'
						)
					
						# Sleep
						time.sleep(15)
						continue

		# Insert data to database
		logging.info('Inserting data into database')
		self._insert_data()

		return self.data


	def user_connections(self, **kwargs):
		'''
		'''

		pass
