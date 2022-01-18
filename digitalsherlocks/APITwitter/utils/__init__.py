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
	Removes local arguments: service, group, timezone, etc.
	Removes None values.

	Returns:
		args
		dict

	'''
	# local arguments
	l = [
		'wd', 'service', 'update_database', 'dbpath', 'dbname',
		'endpoint', 'timezone'
	]

	# adding API keys
	args['tweet_mode'] = 'extended'
	args['count'] = 200

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


