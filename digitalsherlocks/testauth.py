# -*- coding: utf-8 -*-

''' OAuth Twitter API.

'''

# server modules
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# authentication modules
import requests
import webbrowser
from requests_oauthlib import OAuth1, OAuth1Session


# resource credentials
consumer_key = '100nS25Qfq68rYNEKWvniTFK0'
consumer_secret = 'E3tEh23FpQADl4LBYTb3GrI4m6LdI7Zjh8lBVWVlt0J1JPNpR8'

# callback URL
callback_uri = 'http://127.0.0.1:8080/callback'

# server
HOST = ''
PORT = 8080

# HTTP Handler - Render HTML file
class HTTPHandler(BaseHTTPRequestHandler):
	'''
	'''

	def do_GET(self):
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.end_headers()

		# render a HTML file
		f = open('./callback/index.html', 'rb')
		self.wfile.write(f.read())
	
	def log_message(self, format, *args):
		'''
		verbose = False
		'''
		return

# Create server
class Server(threading.Thread):
	'''
	'''
	def run(self):
		'''
		'''
		self.server_object = ThreadingHTTPServer(
			server_address=(HOST, PORT),
			RequestHandlerClass=HTTPHandler
		)
		
		# serve
		self.server_object.serve_forever()

	def stop(self):
		'''
		'''
		# shutdown server
		self.server_object.shutdown()	


# Start server
server_session = Server()
server_session.start()

# OAuth session
session = OAuth1Session(
	client_key=consumer_key,
	client_secret=consumer_secret,
	callback_uri=callback_uri
)

# request oauth tokens
url = 'https://api.twitter.com/oauth/request_token'
fetch_data = session.fetch_request_token(url)
oauth_token = fetch_data['oauth_token']
oauth_token_secret = fetch_data['oauth_token_secret']

# request access tokens
auth_url = f'https://api.twitter.com/oauth/authenticate'
authorization_url = session.authorization_url(
	auth_url,
	request_token=oauth_token
)

# open authorization URL
webbrowser.open(authorization_url)

# verifier
verifier = input('PIN: ').strip()

# stop server
server_session.stop()

print ('')
print ('PIN COLLECTED')
print ('...')
print ('')


# get user metadata
access_token_url = 'https://api.twitter.com/oauth/access_token'
oauth = OAuth1Session(
	client_key=consumer_key,
	client_secret=consumer_secret,
	resource_owner_key=oauth_token,
	resource_owner_secret=oauth_token_secret,
	verifier=verifier,
	callback_uri=callback_uri
)

response = oauth.fetch_access_token(access_token_url)
print ('RESPONSE')
print (response)
print ('...')
print ('')


user_token = response['oauth_token']
user_token_secret = response['oauth_token_secret']
req_params = {'include_email': 'true'}
url_user = 'https://api.twitter.com/1.1/account/verify_credentials.json'

oauth_user = OAuth1Session(
	client_key=consumer_key,
	client_secret=consumer_secret,
	resource_owner_key=user_token,
	resource_owner_secret=user_token_secret
)

user_data = oauth.get(url_user, params=req_params)
print ('USER DATA')
print (user_data.json())
print ('...')
print ('')


# Twitter API connection
from twitter import *

Auth = OAuth(
	user_token, user_token_secret, consumer_key, consumer_secret
)

api = Twitter(auth=Auth)

print ('API')
print (api)
print ('...')
print ('')

# collect data
args = {
	'screen_name': 'DFRLab',
	'count': 5,
	'tweet_mode': 'extended',
	'since_id': 1
}
statuses = api.statuses.user_timeline(**args)
print ('')
print ('')
print ('')
print (statuses)
print ('')
print ('')
