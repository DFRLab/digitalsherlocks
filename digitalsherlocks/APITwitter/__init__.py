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
from APITwitter.store_user_connections import insert_users_data


# API class
class ApiTwitter(object):
	'''
	'''

	# API Default URL
	BASE_URL = 'https://api.twitter.com/1.1'

	def __init__(self, **kwargs):
		'''
		'''

		# Get main arguments
		self.kwargs = kwargs

		# Twitter API user connection
		printl('Twitter user authentication')
		self.TwitterAuth = TwitterAuthentication()
		self.TwitterAPI, self.UAuth = self.TwitterAuth.connect()
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

	def _reset_data(self):
		'''
		'''
		self.data = []


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
			'/friends/list': 'friends',
			'/users/lookup': 'users'
		}

		return src[endpoint_status]

	def _rate_limit_status(self, endpoint_status):
		'''

		Checks rate limits
		'''
		src = self._endpoint_status_parser(endpoint_status)

		# Api URL
		url = f'{self.BASE_URL}/application/rate_limit_status.json'
		res = self.UAuth.get(url, params={'resources': src})

		# Get status
		status = res.json()
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
		if remaining <= 1:
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

		# Adding tweet mode
		self.kwargs['tweet_mode'] = 'extended'

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
		api_url = f'{self.BASE_URL}/statuses/user_timeline.json'
		res = self.UAuth.get(
			api_url, params=self.kwargs
		)

		# Get user timeline
		self.data = res.json()
		if type(self.data) == list and self.data:
			'''

			Insert data
			'''
			self._insert_data()

			# Get max id
			max_id = get_max_id(self.data)
			self.kwargs['max_id'] = max_id

			# Download recent timeline
			update = True
			while update:
				res = self.UAuth.get(
					api_url, params=self.kwargs
				)

				# Statuses
				self.data = res.json()
				if type(self.data) == list and self.data:
					'''

					Insert data
					'''
					self._insert_data()

					# Get max id
					max_id = get_max_id(self.data)
					self.kwargs['max_id'] = max_id

				if type(self.data) == list and not self.data:
					printl('Done')
					printl('Program closed', color='GREEN')
					update = False

				if type(self.data) == dict:
					if 'errors' in self.data.keys():
						e = [
							i['message'] for i in self.data['errors']
						]

						if 'Rate limit exceeded' in e:
							'''

							Sleep application
							'''
							self._sleep_application(
								endpoint_status
							)

							printl('Downloading')
							continue
					else:
						'''

						Dev Diagnosis
						'''
						printl(
							'User timeline < state 2 >',
							color='RED'
						)
						printl('Dev Diagnosis', color='RED')
						printl(f'> {self.data}', color='RED')
						printl('Program closed', color='GREEN')
						update = False

		else:
			if type(self.data) == dict:
				if 'errors' in self.data.keys():
					printl('Errors found', color='RED')
					e = [i['message'] for i in self.data['errors']]
					for message in e:
						printl(f'{message}', color='RED')

					# Close program
					printl('Program closed', color='GREEN')
			else:
				'''

				Dev Diagnosis
				'''
				printl(
					f'No data available for users {u}',
					color='YELLOW'
				)
				printl('User timeline < state 1 >', color='RED')
				printl('Dev Diagnosis', color='RED')
				printl(f'> {self.data}', color='RED')
				printl('Program closed', color='GREEN')
		
		return

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

		# Adding tweet mode
		self.kwargs['tweet_mode'] = 'extended'

		'''

		Query requested
		'''
		q = self.kwargs['q']
		printl(f'Downloading data from query: < {q} >')

		'''

		Check rate limits
		'''
		endpoint_status = '/search/tweets'
		self._sleep_application(endpoint_status)

		'''

		API request

		Endpoint: search tweets
		'''
		api_url = f'{self.BASE_URL}/search/tweets.json'
		res = self.UAuth.get(
			api_url, params=self.kwargs
		)

		# Get tweets
		statuses = res.json()
		if 'statuses' in statuses.keys():
			self.data = statuses['statuses']
			if len(self.data) > 0:
				'''

				Insert data
				'''
				self._insert_data()

				# Get max id
				max_id = get_max_id(self.data)
				self.kwargs['max_id'] = max_id

				# Download recent tweets
				update = True
				while update:
					res = self.UAuth.get(
						api_url, params=self.kwargs
					)

					# Statuses
					statuses = res.json()

					# Get tweets
					if 'statuses' in statuses.keys():
						self.data = statuses['statuses']
						if len(self.data) > 0:
							'''

							Insert data
							'''
							self._insert_data()

							# Get max id
							max_id = get_max_id(self.data)
							self.kwargs['max_id'] = max_id
						else:
							printl('Done')
							printl('Program closed', color='GREEN')
							update = False
					else:
						if 'errors' in statuses.keys():
							e = [
								i['message']
								for i in statuses['errors']
							]

							if 'Rate limit exceeded' in e:	
								'''

								Sleep application
								'''
								self._sleep_application(
									endpoint_status
								)
								printl('Downloading')
							else:
								'''

								Dev Diagnosis
								'''
								printl(
									'Search tweets errors',
									color='RED'
								)
								printl('Dev Diagnosis', color='RED')
								printl(
									f'> {statuses["errors"]}'
								)
								printl(
									'Program closed',
									color='GREEN'
								)

								break
						else:
							'''

							Dev Diagnosis
							'''
							printl(
								'Search tweets < state 2 >',
								color='RED'
							)
							printl('Dev Diagnosis', color='RED')
							printl(f'> {statuses}', color='RED')
							printl('Program closed', color='GREEN')
							
							break
			else:
				printl(
					f'No tweets matching query: < {q} >',
					color='YELLOW'
				)
				printl(
					f'No data was saved',
					color='YELLOW'
				)
				printl('Program closed', color='GREEN')
		else:
			'''

			Dev Diagnosis
			'''
			printl(
				'No statuses in search tweets < state 1 >',
				color='RED'
			)
			printl('Dev Diagnosis', color='RED')
			printl(f'> {statuses}', color='RED')
			printl('Program closed', color='GREEN')

		return

	def _save_friendship_ids(self):
		'''
		'''
		sql = '''
		INSERT INTO ids(
			"id_str"
		) VALUES(
			?
		)
		'''

		# Insert data
		self.db_cursor.executemany(sql, self.data)
		self.db_connection.commit()

	def hydrate_users(self):
		'''

		Pull users' data
		'''
		sql = '''
		SELECT *
		FROM ids
		'''
		self.db_cursor.execute(sql)

		# Get data
		self.data = [
			j for i in self.db_cursor.fetchall() for j in i
		]

		if not self.data:
			printl(f'No data was saved', color='YELLOW')
			printl('Program closed', color='GREEN')
			sys.exit()

		# Building batchs of data
		batch = 100
		ids = [
			self.data[i: i + batch] for i in range(
				0, len(self.data), batch
			)
		]

		'''

		Check rate limits
		'''
		endpoint_status = f'/users/lookup'
		self._sleep_application(endpoint_status)

		# Hydrating users
		printl('Hydrating users')
		api_url = f'{self.BASE_URL}/users/lookup.json'
		for accounts in ids:
			while True:
				res = self.UAuth.get(
					api_url,
					params={user_id: ','.join(accounts)}
				)

				# Get users' data
				self.data = res.json()
				if type(self.data) == list and self.data:
					'''

					Insert data
					'''
					insert_users_data(
						self.db_connection,
						self.db_cursor,
						self.data
					)

					break
				else:
					if type(self.data) == dict:
						if 'errors' in self.data.keys():	
							e = [
								i['message']
								for i in self.data['errors']
							]
							if 'Rate limit exceeded' in e:	
								'''

								Sleep application
								'''
								self._sleep_application(
									endpoint_status
								)
								printl('Hydrating')
						else:
							'''

							Dev Diagnosis
							'''
							printl(
								'Users lookup < state 1 >',
								color='RED'
							)
							printl('Dev Diagnosis', color='RED')
							printl(f'> {self.data}', color='RED')

							break

		return


	def friendships(self):
		'''

		Returns followers and friends of one arbitrary user.

		kwargs:
			- (screen_name | user_id)
			- cursor
			- count
		'''
		# Get type of friendship
		reference = self.kwargs['friendship_type']

		# Clean Twitter arguments
		self.kwargs = clean_twitter_arguments(self.kwargs)

		# Adding parameter
		self.kwargs['stringify_ids'] = True

		'''

		Friendship requested
		'''
		try:
			u = self.kwargs['screen_name']
		except KeyError:
			u = self.kwargs['user_id']

		printl(f'Downloading {reference} from {u}')

		'''

		Check rate limits
		'''
		endpoint_status = f'/{reference}/ids'
		self._sleep_application(endpoint_status)

		'''

		API request

		Endpoint: frienships [followers, friends]
		'''
		api_url = f'{self.BASE_URL}/{reference}/ids.json'
		res = self.UAuth.get(
			api_url, params=self.kwargs
		)

		# Get users' ids
		users = res.json()
		if 'ids' in users.keys():
			self.data = [tuple([i]) for i in users['ids']]
			self._save_friendship_ids()

			# Get cursor
			api_cursor = users['next_cursor']
			while api_cursor != 0:
				self.kwargs['cursor'] = api_cursor
				res = self.UAuth.get(
					api_url, params=self.kwargs
				)

				'''

				Get users data
				'''
				users = res.json()
				if 'ids' in users.keys():
					self.data = [tuple([i]) for i in users['ids']]
					self._save_friendship_ids()

					# Get cursor
					api_cursor = users['next_cursor']
				else:
					if 'errors' in users.keys():
						e = [
							i['message']
							for i in statuses['errors']
						]

						if 'Rate limit exceeded' in e:	
							'''
							Sleep application
							'''	
							self._sleep_application(
								endpoint_status
							)
							printl('Downloading')
					else:
						'''

						Dev Diagnosis
						'''
						printl(
							'No ids in users < state 2 >',
							color='RED'
						)
						printl('Dev Diagnosis', color='RED')
						printl(f'> {users}', color='RED')
						
						break
		else:
			if 'errors' in users.keys():
				printl('Errors found', color='RED')
				e = [i['message'] for i in users['errors']]
				for message in e:
					printl(f'{message}', color='RED')
			else:
				'''

				Dev Diagnosis
				'''
				printl(
					'No ids in users < state 1 >',
					color='RED'
				)
				printl('Dev Diagnosis', color='RED')
				printl(f'> {users}', color='RED')

		# Hydrate users
		self.hydrate_users()

		return
