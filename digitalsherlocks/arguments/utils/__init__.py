# -*- coding: utf-8 -*-

# =========================================
# digitalsherlocks
# A DFRLab project
#
# Author: @estebanpdl
#
# File: Arguments utils.
# =========================================

'''

Functions:

	- aligntext
	- set_working_directory
	- generate_wd
'''

# import modules
import os
import time


# Align text
def aligntext(text):
	'''

	Removes newlines and extra spaces in text
	'''
	return ' '.join(text.split()).strip()

# Set default working directory
def _set_working_directory():
	'''

	Sets a default working directory
	'''

	# get working directory
	cwd = os.getcwd()
	stamp = int(time.time())

	# creating a new working directory
	wd = f'{cwd}/{stamp}/'
	if not os.path.exists(wd):
		os.makedirs(wd, exist_ok=True)

	return wd

# Generate a working directory: default or set by user
def generate_wd(wd):
	'''
	'''
	if wd == None:
		d = _set_working_directory()
	else:
		if wd.endswith('/'):
			wd = wd[:-1]

		stamp = int(time.time())
		d = f'{wd}/{stamp}/'
		if not os.path.exists(d):
			os.makedirs(d, exist_ok=True)

	return d
