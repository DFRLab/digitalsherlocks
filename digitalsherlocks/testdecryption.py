# -*- coding: utf-8 -*-

''' Decrypt keys

'''

# import modules
import json
import requests
from cryptography.fernet import Fernet

# local modules
from config.key import key

# get resource credentials
url = 'https://dfrlab.s3.us-west-2.amazonaws.com/digitalsherlocks/credentials.json'
req = requests.get(url)

credentials = req.json()
consumer_key = credentials['consumer_key']
consumer_secret = credentials['consumer_secret']


# Instance Fernet class
fernet = Fernet(key.encode())

# decrypt
k1decrypt = fernet.decrypt(consumer_key.encode()).decode()
k2decrypt = fernet.decrypt(consumer_secret.encode()).decode()

print (k1decrypt)
print (k2decrypt)
