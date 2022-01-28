# -*- coding: utf-8 -*-

# =========================================
# digitalsherlocks
# A DFRLab project
#
# Author: @estebanpdl
#
# File: Telegram API client.
# =========================================

# import modules
import os
import configparser

# import from modules < authentication >
from telethon import TelegramClient

# Telegram API Authentication
class TelegramAuthentication(object):
	'''
	'''
	def __init__(self, kwargs):
		'''
		'''
		self.app = 'digitalsherlocks'
		self.session_file = 'session_file'
		self.api_id = kwargs['api_id']
		self.api_hash = kwargs['api_hash']

		if not kwargs['phone'].startswith('+'):
			kwargs['phone'] = f'+{kwargs["phone"]}'

		self.phone = kwargs['phone']

	def _save_credentials(self):
		'''

		Write API credentials for future use

			- api id
			- hash
			- phone
			- session file
		'''
		config = configparser.ConfigParser()

		# Creating diectory in users' .config folder
		config_folder = os.path.join(
			os.path.expanduser('~'), '.config', self.app
		)

		if not os.path.exists(config_folder):
			os.makedirs(config_folder, exist_ok=True)

		# Write API credentials
		config.add_section('API')
		config.set(
			'API', 'session_file', self.session_file
		)

		pass

	async def _get_connection(self):
		'''
		'''

		client = TelegramClient(
		)

		pass
