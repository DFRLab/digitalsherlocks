# -*- coding: utf-8 -*-

''' Stores media video data in <media_video> table
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
    a = 'additional_media_info'
    e = 'extended_entities'
    d = 'duration_millis'
    c = 'content_type'
    vid = 'video_info'
    v = 'variants'
    b = 'bitrate'
    m = 'media'

    # create object attrs
    object_attrs = {
        'id': [
            j for obj in data if e in obj.keys()
            for i in obj[e][m] if i['type'] == 'video'
            for j in [i['id']] * len(i[vid][v])
        ],
        'id_str': [
            j for obj in data if e in obj.keys()
            for i in obj[e][m] if i['type'] == 'video'
            for j in [i['id_str']] * len(i[vid][v])
        ],
        'duration_millis': [
            j for obj in data if e in obj.keys()
            for i in obj[e][m] if i['type'] == 'video'
            for j in [i[vid][d]] * len(i[vid][v])
        ],
        'url': [
            j['url'] for obj in data if e in obj.keys()
            for i in obj[e][m] if i['type'] == 'video'
            for j in i[vid][v]
        ],
        'content_type': [
            j[c] for obj in data if e in obj.keys()
            for i in obj[e][m] if i['type'] == 'video'
            for j in i[vid][v]
        ],
        'bitrate': [
            (
                j[b] if b in j.keys() else None
            ) for obj in data if e in obj.keys()
            for i in obj[e][m] if i['type'] == 'video'
            for j in i[vid][v]
        ],
        'monetizable': [
            int(j) for obj in data if e in obj.keys()
            for i in obj[e][m] if i['type'] == 'video'
            for j in [i[a]['monetizable']] * len(i[vid][v])
        ]
    }

    return object_attrs[key]

# process raw data
def get_tweet_data(raw_data):
    ''' Reads raw data and extracts video attrs
    '''
    k = 'media_video'
    db_keys = database_tweet_keys(key=k)

    # main dict
    main = {}
    for key in db_keys:
        attr = process_queries(raw_data, key)
        main[key] = attr
    
    # build dataframe
    data = pd.DataFrame(main)
    data['counter'] = 1

    # process milisecs from video
    data['duration_secs'] = round(
        data['duration_millis'] / 1000, 1
    )
    data['duration_mins'] = round(
        data['duration_millis'] / 60000, 2
    )

    # replace null values by None
    data = data.where((pd.notnull(data)), None)
    
    # order columns
    order = order_columns_to_sql(k)
    return data[order].copy()
    
# insert media video data
def insert_media_video_data(db_connection, cursor, raw_data):
    ''' Inserts media video attrs into <media_video> table
    '''
    data = get_tweet_data(raw_data)
    sql = """
    INSERT INTO media_video(
        "id", "id_str", "duration_millis", "duration_secs", "duration_mins", "url",
        "content_type", "bitrate", "monetizable", "counter"
    ) VALUES(
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
    )
    ON CONFLICT DO NOTHING
    """
    cursor.executemany(sql, tuple(data.values.tolist()))
    db_connection.commit()

    return
