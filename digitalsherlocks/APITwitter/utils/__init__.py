# -*- coding: utf-8 -*-

# =========================================
# digitalsherlocks
# A DFRLab project
#
# Author: @estebanpdl
#
# File: Twitter utils.
# =========================================

# import modules

'''

Twitter utils

Functions:

- clean_twitter_arguments
- get_max_id

'''

def clean_twitter_arguments(args):
	'''

	Cleans twitter arguments.
	Removes local argument: timezone
	Removes None values.

	Returns:
		args
		dict

	'''
	# reference
	l = ['timezone']

	# add tweet mode key
	args['tweet_mode'] = 'extended'

	# filter keys
	return {
		k:v for k, v in args.items() if k not in l and v != None
	}

def get_max_id(statuses):
	'''

	Get max id in a set of tweets

	Returns:
		max_id
		int
	'''
	return min([i['id'] for i in statuses]) - 1


