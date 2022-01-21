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

# import log utils
from logs import printl

'''

import storage <tmp code>

TODO: Storage class.
'''
from APITwitter.storage import insert_data


# API class
class ApiTwitter(object):
	'''
	'''

	def __init__(self, **kwargs):
		'''
		'''

		# Get main arguments
		self.kwargs = kwargs

		# Twitter API user connection
		printl('Twitter user authentication')
		self.TwitterAuth = TwitterAuthentication()
		self.TwitterAPI = self.TwitterAuth.connect()
		printl('Authentication completed', color='BLUE')

		# Twitter API connection - retries
		self.max_retries = self.kwargs['max_retries']

		# Get working directory
		self.wd = self.kwargs['wd']

		# Requested attrs
		self.timezone = self.kwargs['timezone'] \
			if 'timezone' in self.kwargs.keys() else None

		# Get database-related arguments
		self.update_database = self.kwargs['update_database']
		self.dbpath = self.kwargs['dbpath']
		self.dbname = self.kwargs['dbname']

		# Twitter endpoints
		self.endpoint = self.kwargs['endpoint']

		# Build database arguments
		printl('Building database arguments')
		self.db_args = {
			'wd': self.wd,
			'update_database': self.update_database,
			'dbpath': self.dbpath,
			'dbname': self.dbname,
			'endpoint': self.endpoint
		}

		# Database instance
		self.db = Database(**self.db_args)
		self.db_connection, self.db_cursor = self.db._connect_db()


		# Collected data
		self.data = []
		self.partial_data = False

	def _insert_data(self):
		'''

		Inserts data into database.
		'''

		# Insert data
		insert_data(
			self.db_connection,
			self.db_cursor,
			self.data,
			self.timezone
		)

	def _connection_retry(self, max_retries):
		'''
		'''
		sleep_for = 15
		if max_retries > 0:
			printl('Retrying...')
			printl(
				f'Max Retries: 10. LEFT {self.max_retries}'
			)

			# Sleep
			time.sleep(sleep_for)

			# Increasing sleep value
			sleep_for += sleep_for

			# Update data
			if self.data:
				self.kwargs['max_id'] = get_max_id(
					self.data
				)

				return True
		else:
			return False

	def _handle_twitter_error(self, e):
		'''

		Handles TwitterError and TwitterHTTPError.
		'''
		error = e.__class__.__name__
		e_type, e_value, e_traceback = sys.exc_info()

		if error == 'TwitterError':
			# Retry < API request failed >
			if 'Incomplete JSON data' in str(e_value):
				printl(
					'TwitterError. Connection error',
					color='RED'
				)

				# Decrease MAX RETRIES
				self.max_retries -= 1

				# Retry
				retry_status = self._connection_retry(
					self.max_retries
				)

				return error, retry_status

	def _endpoint_status_parser(self, endpoint_status):
		'''

		Returns rate limit status' key (i.e. statuses, friends, etc.)
		'''

		src = {
			'/statuses/user_timeline': 'statuses',
			'/search/tweets': 'search',
			'/followers/ids': 'followers',
			'/followers/list': 'followers',
			'/friends/ids': 'friends',
			'/friends/list': 'friends'
		}

		return src[endpoint_status]

	def _rate_limit_status(self, endpoint_status):
		'''

		Checks rate limits
		'''
		src = self._endpoint_status_parser(endpoint_status)

		status = self.TwitterAPI.application.rate_limit_status()
		resource = status['resources'][src][endpoint_status]

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
			printl(
				'Application reached rate limits.',
				color='YELLOW'
			)
			printl(
				f'Sleeping application for {sleep_for} secs...'
			)

			# Sleep application
			time.sleep(sleep_for)

			# Awake
			printl('Awake', color='GREEN')

	'''

	Build Twitter API endpoints
	'''
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

		Log requested user
		'''
		try:
			u = self.kwargs['screen_name']
		except KeyError:
			u = self.kwargs['user_id']

		printl(f'Downloading timeline from user {u}')

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
						statuses = \
							self.TwitterAPI.statuses.user_timeline(
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
					if 'Incomplete JSON data' in str(e_value):
						printl(
							'TwitterError. Connection error',
							color='RED'
						)

						# Decrease MAX RETRIES
						self.max_retries -= 1

						# Retry
						retry_status = self._connection_retry(
							self.max_retries
						)

						if retry_status:
							continue
						else:
							if self.data:
								self.partial_data = True
								break
							else:
								'''
								Quit program
								'''
								printl(
									'API Twitter Error',
									color='RED'
								)
								printl(
									'Ending program. Try again',
									color='RED'
								)

								sys.exit()


				if error == 'TwitterHTTPError':
					exceed_api_limit = True

					# sleep application
					self._sleep_application(endpoint_status)

					continue

		

		
		# Partial data only
		if self.partial_data:
			printl('After twitter errors, API returned partial data')
			printl(
				f'Tweets collected: {len(self.data)}',
				color='BLUE'
			)
			
		# Insert data to database
		printl('Inserting data into database')
		self._insert_data()
		
		return self.data
	
	def search_tweets(self):
		'''

		Returns a collection of relevant Tweets matching a
		specified query.

		kwargs:
			- q [query]
			- geocode
			- lang
			- result_type
			- count
			- until
			- since_id
			- max_id
			- include_entities
		'''
		# Clean Twitter arguments
		self.kwargs = clean_twitter_arguments(self.kwargs)

		'''

		Query requested
		'''
		q = self.kwargs['q']
		printl(f'Downloading data from query {q}')

		'''

		Check rate limits
		'''
		endpoint_status = '/search/tweets'
		self._sleep_application(endpoint_status)

		'''

		API request

		Endpoint: search tweets
		'''
		while True:
			try:
				statuses = self.TwitterAPI.search.tweets(
					**self.kwargs
				)
				statuses = statuses['statuses']
				if len(statuses) > 0:
					self.data.extend(statuses)
					max_id = get_max_id(statuses)

					# Download more data
					while len(statuses) > 0:
						self.kwargs['max_id'] = max_id
						statuses = self.TwitterAPI.search.tweets(
							**self.kwargs
						)

						#  Get statuses
						statuses = statuses['statuses']
						if len(statuses) > 0:
							max_id = get_max_id(statuses)
							self.data.extend(statuses)

					break
			
			except (TwitterHTTPError, HTTPError, TwitterError) as e:
				



				error = e.__class__.__name__
				e_type, e_value, e_traceback = sys.exc_info()

				if error == 'TwitterError':

					# Retry < API request failed >
					if 'Incomplete JSON data' in str(e_value):
						printl(
							'TwitterError. Connection error',
							color='RED'
						)

						# Decrease MAX RETRIES
						self.max_retries -= 1

						# Retry
						retry_status = self._connection_retry(
							self.max_retries
						)

						if retry_status:
							continue
						else:
							if self.data:
								self.partial_data = True
								break
							else:
								'''
								Quit program
								'''
								printl(
									'API Twitter Error',
									color='RED'
								)
								printl(
									'Ending program. Try again',
									color='RED'
								)

								sys.exit()

				if error == 'TwitterHTTPError':
					exceed_api_limit = True

					# sleep application
					self._sleep_application(endpoint_status)

					continue

		# Partial data only
		if self.partial_data:
			printl('After twitter errors, API returned partial data')
			printl(
				f'Tweets collected: {len(self.data)}',
				color='BLUE'
			)

		# Insert data to database
		printl('Inserting data into database')
		self._insert_data()
		
		return self.data

	def friendships(self):
		'''

		Returns followers and friends of one arbitrary user.

		kwargs:
			- (screen_name | user_id)
			- cursor
			- count
		'''
		# Add parameter
		self.kwargs['stringify_ids'] = True

		# Get type of friendship
		# reference = self.kwargs['friendship_type']

		'''

		Check rate limits
		'''
		# endpoint_status = f'/{reference}/ids'
		# self._sleep_application(endpoint_status)

		'''

		TODO: improve connection
		'''
		# if reference == 'followers':
		# 	users = self.TwitterAPI.followers.ids(**self.kwargs)
		# else:
		# 	users = self.TwitterAPI.friends.ids(**self.kwargs)

		# '''

		# Save ids in sql table
		# '''

		return True
