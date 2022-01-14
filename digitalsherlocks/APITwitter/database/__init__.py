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
import sqlite3
import requests

# Database class
class Database(object):
	'''
	'''
	def _get_sqlfile(self, sql_file):
		'''
		'''
		# Get SQL file
		path = f'digitalsherlocks/sql/{sql_file}.sql'
		url = f'https://dfrlab.s3.us-west-2.amazonaws.com/{path}'

		# URL Request
		return requests.get(url).text

	def _connect_db(self, **kwargs):
		'''
		'''
		# Get variables
		db_path = kwargs['db_path']
		sql_file = kwargs['sql_file']
		update_existing_db = kwargs['update_existing_db']

		# Connect database
		db_connection = sqlite3.connect(db_path)

		# Get cursor
		db_cursor = db_connection.cursor()

		if not update_existing_db:

			# Encoding database
			db_cursor.execute('PRAGMA encoding')

			# Execute script
			sql_script = self._get_sqlfile(sql_file)
			db_cursor.executescript(sql_script)

			# Commit results
			db_connection.commit()

		return db_connection, db_cursor

