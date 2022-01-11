# -*- coding: utf-8 -*-

''' Stores mentions attrs in <mentions> table
'''

# import modules
import pandas as pd
import json

# import database keys
from assets import database_tweet_keys, order_columns_to_sql

# creating functions
def process_queries(data, key):
    ''' Creates a list comprehesion based on data and key
    '''
    # main keys
    e = 'entities'
    user = 'user'
    screen_name = 'screen_name'
    rstatus = 'retweeted_status'
    user_mentions = 'user_mentions'

    # helpers
    def query_a(data, k):
        ''' Returns data from user - tweet owner
        '''
        return [
            i for obj in data for i in [obj[user][k]] * len(obj[e][user_mentions])
            if len(obj[e][user_mentions]) > 0 and not rstatus in obj.keys()
        ]
    
    def query_b(data, k):
        ''' Returns mention data - the user mentioned by the tweet owner
        '''
        return [
            i[k] for obj in data for i in obj[e][user_mentions]
            if len(obj[e][user_mentions]) > 0 and not rstatus in obj.keys()
        ]
    
    # create object attrs
    object_attrs = {
        'id_from_user': query_a(data, 'id'),
        'id_str_from_user': query_a(data, 'id_str'),
        'screen_name_from_user': query_a(data, screen_name),
        'id_user': query_b(data, 'id'),
        'id_str_user': query_b(data, 'id_str'),
        'screen_name_user': query_b(data, screen_name)
    }
    if key in object_attrs.keys():
        return object_attrs[key]
    else:
        return [
            i for obj in data for i in [obj[key]] * len(obj[e][user_mentions])
            if len(obj[e][user_mentions]) > 0 and not rstatus in obj.keys()
        ]

# process raw data
def get_tweet_data(raw_data):
    ''' Reads raw data and extracts mentions attrs
    '''    
    k = 'mentions'
    db_keys = database_tweet_keys(key=k)

    # main dict
    main = {}
    for key in db_keys:
        attr = process_queries(raw_data, key)
        main[key] = attr
    
    # build dataframe
    data = pd.DataFrame(main)
    data['counter'] = 1

    # replace null values by None
    data = data.where((pd.notnull(data)), None)
    
    # order columns
    order = order_columns_to_sql(k)
    return data[order].copy()

# insert mentions attrs
def insert_mentions_data(db_connection, cursor, raw_data):
    ''' Inserts mentions attrs into <mentions> table
    '''
    data = get_tweet_data(raw_data)
    sql = """
    INSERT INTO mentions(
        "id", "id_str", "id_from_user", "id_str_from_user", "screen_name_from_user",
        "id_user", "id_str_user", "screen_name_user", "counter"
    ) VALUES(
        ?, ?, ?, ?, ?, ?, ?, ?, ?
    )
    ON CONFLICT DO NOTHING
    """
    cursor.executemany(sql, tuple(data.values.tolist()))
    db_connection.commit()

    return
