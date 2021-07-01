# -*- coding: utf-8 -*-

''' Stores place data in <place> table
'''

# import modules
import json
import pandas as pd

# import local modules
from utils import to_string

# import database keys
from assets import database_tweet_keys, order_columns_to_sql

# creating functions
def process_queries(data, key):
	'''  Creates a list comprehesion based on data and key.
	'''
	# main keys
	k = 'place'
	b = 'bounding_box'
	t = 'type'
	geo = 'coordinates'

	# create object
	object_attrs = {
		'type': [(
				obj[k][b][t] if obj[k][b] != None else None
			)
			for obj in data if obj[k] != None
		],
		'coordinates': [(
				obj[k][b][geo] if obj[k][b] != None else None
			)
			for obj in data if obj[k] != None
		]
	}
	if key in object_attrs.keys():
		return object_attrs[key]
	else:
		return [obj[k][key] for obj in data if obj[k] != None]

# process fields
def process_fields(key):
	''' Returns a function which process and modify data based on key
	'''
	obj = {
		'coordinates': to_string
	}
	for k, function in obj.items():
		if key == k:
			return function
	
	return False

# process raw data
def get_tweet_data(raw_data):
    ''' Reads raw data and extracts place attrs
    '''
    k = 'place'
    db_keys = database_tweet_keys(key=k)

    # main dict
    main = {}
    for key in db_keys:
        attr = process_queries(raw_data, key)
        main[key] = attr
        function = process_fields(key)
        if function:
            main[key] = function(main[key])
    
    data = pd.DataFrame(main)
    data = data.where((pd.notnull(data)), None)
    
    # order columns
    order = order_columns_to_sql(k)
    return data[order].copy()

# insert place attrs
def insert_place_data(db_connection, cursor, raw_data):
	''' Inserts place attrs into <place> table
	'''
	data = get_tweet_data(raw_data)
	sql = """
	INSERT INTO place(
		"id", "name", "full_name", "country", "country_code", "place_type",
		"type", "coordinates"
	) VALUES(
		?, ?, ?, ?, ?, ?, ?, ?
	)
	ON CONFLICT (id) DO NOTHING
	"""
	cursor.executemany(sql, tuple(data.values.tolist()))
	db_connection.commit()

	return
