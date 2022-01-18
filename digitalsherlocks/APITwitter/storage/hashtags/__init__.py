# -*- coding: utf-8 -*-

''' Stores hashtags attrs in <hashtags> table
'''

# import modules
import pandas as pd
import json

# import database keys
from APITwitter.assets import database_tweet_keys, order_columns_to_sql

# creating functions
def process_queries(data, key):
    ''' Creates a list comprehesion based on data and key
    '''
    # main keys
    screen_name = 'screen_name'
    h = 'hashtags'
    e = 'entities'
    user = 'user'
    t = 'text'

    # helpers
    def query(data, k):
        ''' Return hashtags data
        '''
        return [
            i for obj in data for i in [obj[user][k]] * len(obj[e][h])
            if len(obj[e][h]) > 0
        ]
    
    # create object attrs
    object_attrs = {
        'id_from_user': query(data, 'id'),
        'id_str_from_user': query(data, 'id_str'),
        'screen_name_from_user': query(data, screen_name),
        'hashtag': [
            i[t] for obj in data for i in obj[e][h]
            if len(obj[e][h]) > 0
        ]
    }
    if key in object_attrs.keys():
        return object_attrs[key]
    else:
        return [
            i for obj in data for i in [obj[key]] * len(obj[e][h])
            if len(obj[e][h]) > 0
        ]

# process raw data
def get_tweet_data(raw_data):
    ''' Reads raw data and extracts hashtags attrs
    '''    
    k = 'hashtags'
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

# insert hashtags attrs
def insert_hashtags_data(db_connection, cursor, raw_data):
    '''
    '''
    data = get_tweet_data(raw_data)
    sql = """
    INSERT INTO hashtags(
        "id", "id_str", "id_from_user", "id_str_from_user",
        "screen_name_from_user", "hashtag", "counter"
    ) VALUES (
        ?, ?, ?, ?, ?, ?, ?
    )
    ON CONFLICT DO NOTHING
    """
    cursor.executemany(sql, tuple(data.values.tolist()))
    db_connection.commit()

    return

