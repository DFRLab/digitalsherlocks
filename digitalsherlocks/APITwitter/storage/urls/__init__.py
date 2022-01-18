# -*- coding: utf-8 -*-

''' Stores urls attrs in <urls> table
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
    e = 'entities'
    url = 'url'
    urls = 'urls'
    exp_url = 'expanded_url'

    # create object attrs
    object_attrs = {
        url: [
            i[url] for obj in data for i in obj[e][urls]
            if len(obj[e][urls]) > 0
        ],
        exp_url: [
            i[exp_url] for obj in data for i in obj[e][urls]
            if len(obj[e][urls]) > 0
        ]
    }
    if key in object_attrs.keys():
        return object_attrs[key]
    else:
        return [
            i for obj in data
            for i in [obj[key]] * len(obj[e][urls])
            if len(obj[e][urls]) > 0
        ]

# process raw data
def get_tweet_data(raw_data):
    ''' Reads raw data and extracts urls attrs
    '''
    k = 'urls'
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

# insert urls data
def insert_urls_data(db_connection, cursor, raw_data):
    ''' Inserts ulrs attrs into <urls> table
    '''
    data = get_tweet_data(raw_data)
    sql = """
    INSERT INTO urls(
        "id", "id_str", "url", "expanded_url", "counter"
    ) VALUES(
        ?, ?, ?, ?, ?
    )
    ON CONFLICT DO NOTHING
    """
    cursor.executemany(sql, tuple(data.values.tolist()))
    db_connection.commit()

    return
