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
				print (
					f'The file {self.dbpath} was not found.'
				)
				print (
					'Please try again with the correct file.'
				)

				# Quit program
				sys.exit()
			else:
				dbfile = self.dbpath

		return dbfile

	def _connect_db(self):
		'''

		Connects to sqlite database
		'''
		# Get database filename
		dbfile = self._get_database_filename()

		# Connect database
		db_connection = sqlite3.connect(dbfile)

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

			'''

			Add --> ABS PATH for dbfile

			print ('')
			print (f'Database created at {dbfile}')
			print ('')
			'''

		'''
		ELSE
		
		LOG RESPONSE

		GET ARGUMENTS FROM THE EXISTING DATABASE, IF NEEDED
			GET ENDPOINT. WHICH ENDPOINT WILL BE CALLED????
		'''

		return db_connection, db_cursor
