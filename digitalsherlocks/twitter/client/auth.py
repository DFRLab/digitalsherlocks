# -*- coding: utf-8 -*-

# =========================================
# digitalsherlocks
# A DFRLab project - @estebanpdl
# =========================================

'''

Twitter User Authentication

'''

# import server modules
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# import authentication modules
import webbrowser
from requests_oauthlib import OAuth1, OAuth1Session


# HTTP Handler - Render HTML file
class TwitterAuthentication:
	'''
	'''

	return