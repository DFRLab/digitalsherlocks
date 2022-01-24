# -*- coding: utf-8 -*-

# =========================================
# digitalsherlocks
# A DFRLab project
#
# Author: @estebanpdl
#
# File: Manages local database.
# =========================================

# import modules
import os
import sys
import sqlite3
import requests

# import log utils
from logs import printl

# import from modules
from sqlite3 import OperationalError

# Database class
class Database(object):
	'''
	'''
	def __init__(self, **kwargs):
		'''

		kwargs:
			- wd
				[working directory]
			- update_database
				[if an existing database needs to be updated]
			- dbpath
				[Existing database]
			- dbname
				[Custom database name]
			- endpoint
				[Which SQL file will be readed]
		'''

		# Instance variables
		self.wd = kwargs['wd']
		self.update_database = kwargs['update_database']
		self.dbpath = kwargs['dbpath']
		self.dbname = kwargs['dbname']
		self.endpoint = kwargs['endpoint']

	def _get_sqlfile(self):
		'''

		Reads a sql file hosted on AWS s3.
		'''
		path = f'digitalsherlocks/sql/{self.endpoint}.sql'
		url = f'https://dfrlab.s3.us-west-2.amazonaws.com/{path}'

		# URL Request
		return requests.get(url).text

	def _get_database_filename(self):
		'''

		Gets database filename.
		'''
		if self.dbpath == None:
			name = 'data' if self.dbname == None else self.dbname
			dbfile = f'{self.wd}{name}.db'

		else:
			isfile = os.path.isfile(self.dbpath)
			if not isfile and self.update_database == True:
				printl(
					f'The file {self.dbpath} was not found.',
					color='RED'
				)
				printl(
					'Please try again with the correct file.',
					color='RED'
				)
				printl('Program closed', color='GREEN')

				# Quit program
				sys.exit()
			else:
				dbfile = self.dbpath

		dbfile = os.path.abspath(dbfile)
		return dbfile.replace(os.sep, '/')

	def _get_db_attrs(self, data):
		'''

		Gets data from _return_database_attrs.
		If tweets, argument will be q < query >
		If users, argument will be user_id. Will update database
			based on the user id.
		'''
		obj = {
			'tweets': 'q',
			'users': 'user_id'
		}

		args = []
		for item in data:
			tmp = {
				obj[item[1]]: item[0] if item[4] == None else item[4],
				'endpoint': item[1],
				'since_id': item[2],
				'timezone': item[3]
			}

			# append args
			args.append(tmp)

		return args

	def _return_database_attrs(self, db_connection, db_cursor):
		'''

		Gets database attrs.
		Return: dict < kwargs >
		'''
		sql = '''
		SELECT
			search_request, endpoint_type, MAX(id), timezone,
			CASE WHEN endpoint_type = 'users'
				THEN user_id
				ELSE NULL
			END
		FROM tweet
		GROUP BY search_request
		'''
		try:
			db_cursor.execute(sql)
		except OperationalError:
			'''

			Error found. Incorrect database.
			'''
			db_cursor.execute("PRAGMA database_list")
			rows = db_cursor.fetchall()

			# Get main db
			main_db = [
				i[2] for i in rows if i[1] == 'main' and i[2] != None
			][0]

			# Transform db path
			main_db = main_db.replace(os.sep, '/')

			printl(
				f'Error found: Incorrect database: {main_db}',
				color='RED'
			)
			printl(
				'Database should contain tweets or user timelines',
				color='RED'
			)
			printl(
				'Please try again with the correct file.',
				color='RED'
			)
			printl('Program closed', color='GREEN')
			
			
			# Quit program
			sys.exit()


		# Get data
		data = [i for i in db_cursor.fetchall()]

		return self._get_db_attrs(data) 

	def _connect_db(self):
		'''

		Connects to sqlite database
		'''
		# Get database filename
		dbfile = self._get_database_filename()
		printl(f'Database at {dbfile}', color='GREEN')

		# Connect database
		printl('Connecting to database')
		db_connection = sqlite3.connect(dbfile)
		printl('Database connected')

		# Get database cursor
		db_cursor = db_connection.cursor()

		'''
		Database status:

			- Check if an existing database will be updated.
		'''

		if not self.update_database:

			# Encoding database
			db_cursor.execute('PRAGMA encoding')

			# Execute SQL script
			sql_script = self._get_sqlfile()			
			db_cursor.executescript(sql_script)

			# Commit results
			db_connection.commit()

		return db_connection, db_cursor
