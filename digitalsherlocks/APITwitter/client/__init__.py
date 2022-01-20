# -*- coding: utf-8 -*-

# =========================================
# digitalsherlocks
# A DFRLab project
#
# Author: @estebanpdl
#
# File: Twitter user authentication.
# =========================================


'''

Twitter User Authentication

'''

# import modules
import os
import configparser

# import server modules
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# import authentication modules
import requests
import webbrowser

# import from modules < authentication >
from APITwitter.config.key import key
from twitter import OAuth, Twitter
from cryptography.fernet import Fernet
from requests_oauthlib import OAuth1, OAuth1Session

# import log utils
from logs import printl

# HTTP Handler - Render HTML file
class HTTPHandler(BaseHTTPRequestHandler):
	'''
	
	GET request
	Renders HTML file
	
	'''
	def do_GET(self):
		'''
		GET request
		'''
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.end_headers()

		# Render HTML file
		path = 'digitalsherlocks/callback/index.html'
		url = f'https://dfrlab.s3.us-west-2.amazonaws.com/{path}'
		
		# Get HTML file
		fp = requests.get(url)		
		self.wfile.write(fp.text.encode())

	def log_message(self, format, *args):
		'''

		Remove logs
		'''
		return


# Create Server
class Server(threading.Thread):
	'''

	Allows run and stop server
	'''

	# Server localhost and port
	HOST = ''
	PORT = 8080

	def run(self):
		'''

		Run server
		'''
		self.server_object = ThreadingHTTPServer(
			server_address=(self.HOST, self.PORT),
			RequestHandlerClass=HTTPHandler
		)

		# Serve
		self.server_object.serve_forever()

	def stop(self):
		'''
		
		Shutdown server
		'''
		self.server_object.shutdown()


# Manage API credentials
class ManageAPICredentials(object):
	'''

	Gets Twitter API credentials
	'''

	def __init__(self, req):
		'''
		'''
		self.req = req
		self.key = key

		# get credentials
		self.credentials = self.req.json()
		self.fernet = Fernet(self.key.encode())

		# API keys
		self.consumer_key = self.credentials['consumer_key']
		self.consumer_secret = self.credentials['consumer_secret']


	def decrypt(self):
		'''
		'''
		k1 = self.fernet.decrypt(self.consumer_key.encode())
		k2 = self.fernet.decrypt(self.consumer_secret.encode())

		return k1.decode(), k2.decode()


# Twitter user authentication
class TwitterAuthentication(object):
	'''
	
	Twitter User Authentication
	'''

	# Request API credentials

	'''

	URL attrs
	'''
	PATH = 'digitalsherlocks/access/credentials.json'

	# URL request
	URL = f'https://dfrlab.s3.us-west-2.amazonaws.com/{PATH}'
	REQ = requests.get(URL)

	# Twitter API credentials
	API_CREDENTIALS = ManageAPICredentials(REQ)
	CONSUMER_KEY, CONSUMER_SECRET = API_CREDENTIALS.decrypt()

	# Server session
	SERVER_SESSION = Server()


	def __init__(self):
		'''
		'''
		# Twitter API session
		self.consumer_key = self.CONSUMER_KEY
		self.consumer_secret = self.CONSUMER_SECRET
		self.callback_uri = 'http://127.0.0.1:8080/callback'
		self.session = None

		# User API access
		self.verifier = None
		self.api_access = None

		# Digitalsherlocks
		self.app = 'digitalsherlocks'

	def _api_session(self):
		'''

		Creates a API session using consumer API credentials
		'''

		# Start Localhost server
		self.SERVER_SESSION.start()

		# API session
		return OAuth1Session(
			client_key=self.consumer_key,
			client_secret=self.consumer_secret,
			callback_uri=self.callback_uri
		)

	def _request_oauth_token(self):
		'''
		'''
		url = 'https://api.twitter.com/oauth/request_token'
		self.session = self._api_session()

		# Fetch data
		fetch_data = self.session.fetch_request_token(url)
		oauth_token = fetch_data['oauth_token']
		oauth_token_secret = fetch_data['oauth_token_secret']

		return oauth_token, oauth_token_secret

	def _get_access_tokens(self, **kwargs):
		'''
		'''
		url = 'https://api.twitter.com/oauth/access_token'
		oauth = OAuth1Session(
			client_key=self.consumer_key,
			client_secret=self.consumer_secret,
			resource_owner_key=kwargs['oauth_token'],
			resource_owner_secret=kwargs['oauth_token_secret'],
			verifier=kwargs['verifier'],
			callback_uri=self.callback_uri
		)

		res = oauth.fetch_access_token(url)
		return {
			'user_token': res['oauth_token'],
			'user_token_secret': res['oauth_token_secret']
		}

	def _save_api_tokens(self, tokens):
		'''

		Write API keys for future use
			- User token
			- User token secret
		'''
		config = configparser.ConfigParser()

		# Creating diectory in users' .config folder
		config_folder = os.path.join(
			os.path.expanduser('~'), '.config', self.app
		)
		if not os.path.exists(config_folder):
			os.makedirs(config_folder, exist_ok=True)

		# Write API keys
		config.add_section('API')
		config.set(
			'API', 'token', tokens['user_token']
		)
		config.set(
			'API', 'token_secret', tokens['user_token_secret']
		)

		# Config file
		config_file = f'{config_folder}/apitwitter.ini'
		with open(config_file, mode='w', encoding='utf-8') as f:
			config.write(f)

	def _request_user_verification(self):
		'''
		'''
		# Get session API tokens
		oauth_token, oauth_token_secret = self._request_oauth_token()

		url = 'https://api.twitter.com/oauth/authenticate'
		authorization_url = self.session.authorization_url(
			url=url,
			request_token=oauth_token
		)

		# Open authorization URL
		webbrowser.open(authorization_url)

		# Get verifier
		printl('Input required', color='BLUE')
		self.verifier = input(
			f'{log_time_fmt()} - Please, copy and add PIN: '
		).strip()

		# Stop Localhost server
		self.SERVER_SESSION.stop()

		# Get access tokens
		params = {
			'oauth_token': oauth_token,
			'oauth_token_secret': oauth_token_secret,
			'verifier': self.verifier
		}

		user_access_tokens = self._get_access_tokens(**params)

		# Save API keys
		self._save_api_tokens(user_access_tokens)

		return {
			'token': user_access_tokens['user_token'],
			'token_secret': user_access_tokens['user_token_secret'],
			'consumer_key': self.consumer_key,
			'consumer_secret': self.consumer_secret
		}

	def connect(self):
		'''
		'''
		config_folder = os.path.join(
			os.path.expanduser('~'), '.config', self.app
		)
		config_file = f'{config_folder}/apitwitter.ini'
		if os.path.isfile(config_file):
			'''

			Read api.ini file
			'''
			config = configparser.ConfigParser()
			config.read(config_file)

			# Build api access
			self.api_access = {
				'token': config['API']['token'],
				'token_secret': config['API']['token_secret'],
				'consumer_key': self.consumer_key,
				'consumer_secret': self.consumer_secret
			}
		else:
			# Build api acces via user authentication
			self.api_access = self._request_user_verification()
		
		# Connect to Twitter API
		Auth = OAuth(**self.api_access)
		return Twitter(auth=Auth)
