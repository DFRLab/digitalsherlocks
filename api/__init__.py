# -*- coding: utf-8 -*-

''' Connects to twitter api.

	- Gets twitter data.
'''

# import local module
from api.keywords import keyword_api
from api.profiles import profile_api
from api.user_connections import user_connection

# main function API
def api(db_connection, cursor, type_of_query, kwargs):
	'''
	type_of_query: string -> keyword or profile

	kwargs: for type_of_query:
		kerword:
			query
        	lang
       		res_type
        	timezone
        	geocode
        	since_id
			tweet_mode
		profile:
			screen_name
        	exclude_replies
        	include_rts
        	timezone
        	since_id
        	tweet_mode
	'''
	if type_of_query == 'keyword':
		api_connection = keyword_api(db_connection, cursor, **kwargs)
	elif type_of_query == 'profile':
		api_connection = profile_api(db_connection, cursor, **kwargs)
	else:
		api_connection = user_connection(db_connection, cursor, **kwargs)

	return api_connection
