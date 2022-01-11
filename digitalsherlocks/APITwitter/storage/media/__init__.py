# -*- coding: utf-8 -*-

''' Stores media attrs in <media> table
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
    e = 'extended_entities'
    m = 'media'

    return [
        i[key] for obj in data
        if e in obj.keys() for i in obj[e][m]
    ]

# process raw data
def get_tweet_data(raw_data):
    ''' Reads raw data and extracts media attrs
    '''
    k = 'media'
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

# insert media attrs
def insert_media_data(db_connection, cursor, raw_data):
    ''' Inserts media attrs into <media> table
    '''
    data = get_tweet_data(raw_data)
    sql = """
    INSERT INTO media(
        "id", "id_str", "url", "expanded_url", "media_url_https", "type", "counter"
    ) VALUES(
        ?, ?, ?, ?, ?, ?, ?
    )
    ON CONFLICT DO NOTHING
    """
    cursor.executemany(sql, tuple(data.values.tolist()))
    db_connection.commit()

    return

