# -*- coding: utf-8 -*-

''' Stores media tweet relationship in <media_tweet> table
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
    i = 'id'
    istr = 'id_str'
    e = 'entities'
    m = 'media'

    # create object attrs
    object_attrs = {
        'id_media': [
            item[i] for obj in data if m in obj[e].keys()
            for item in obj[e][m]
        ],
        'id_str_media': [
            item[istr] for obj in data if m in obj[e].keys()
            for item in obj[e][m]
        ]
    }
    if key in object_attrs.keys():
        return object_attrs[key]
    else:
        return [
            item for obj in data if m in obj[e].keys()
            for item in [obj[key]] * len(obj[e][m])
        ]

# process raw data
def get_tweet_data(raw_data):
    ''' Reads raw data and creates media tweet relationship
    '''
    k = 'media_tweet'
    db_keys = database_tweet_keys(key=k)

    # main dict
    main = {}
    for key in db_keys:
        attr = process_queries(raw_data, key)
        main[key] = attr
    
    # build dataframe
    data = pd.DataFrame(main)

    # replace null values by None
    data = data.where((pd.notnull(data)), None)
    
    # order columns
    order = order_columns_to_sql(k)
    return data[order].copy()

# insert media tweet data
def insert_media_tweet_data(db_connection, cursor, raw_data):
    ''' Inserts media tweet relationship into <media_tweet> table
    '''
    data = get_tweet_data(raw_data)
    sql = """
    INSERT INTO media_tweet(
        "id", "id_str", "id_media", "id_str_media"
    ) VALUES(
        ?, ?, ?, ?
    )
    ON CONFLICT DO NOTHING
    """
    cursor.executemany(sql, tuple(data.values.tolist()))
    db_connection.commit()

    return
