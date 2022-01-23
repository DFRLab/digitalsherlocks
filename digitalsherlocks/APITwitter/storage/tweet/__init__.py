# -*- coding: utf-8 -*-

''' Stores tweet data in <tweet> table
'''

# import modules
import pandas as pd
import json

# import local modules
from utils import clean_text, get_tweet_source, timestamp_attrs, bag_of_words, \
    to_string

# import database keys
from APITwitter.assets import database_tweet_keys, order_columns_to_sql

# creating functions
def process_queries(data, key):
    ''' Creates a list comprehesion based on data and key
    '''
    # main keys
    i = 'id'
    istr = 'id_str'
    rstatus = 'retweeted_status'
    txt = 'full_text'
    user = 'user'
    screen_name = 'screen_name'
    isqt = 'is_quote_status'
    qstr = 'quoted_status_id_str'
    isrt = 'is_retweet_status'
    metadata = 'metadata'
    iso_lang = 'iso_language_code'
    lang = 'lang'
    place = 'place'

    # create object attrs
    object_attrs = {
        'text': [
            obj[txt] for obj in data
        ],
        'full_text': [
            (
                obj[rstatus][txt]
                if rstatus in obj.keys() else obj[txt]
            ) for obj in data
        ],
        screen_name: [
            obj[user][screen_name] for obj in data
        ],
        'user_id': [
            obj[user][i] for obj in data
        ],
        'user_id_str': [
            obj[user][istr] for obj in data
        ],
        isqt: [
            int(obj[isqt]) for obj in data
        ],
        'quoted_status_id_str': [
            (
                obj[qstr]
                if obj[isqt] == True and qstr in obj.keys()
                else None
            ) for obj in data
        ],
        isrt: [
            (
                1 if rstatus in obj.keys() else 0
            ) for obj in data
        ],
        'rt_user_screen_name': [
            (
                obj[rstatus][user][screen_name]
                if rstatus in obj.keys() else None
            ) for obj in data
        ],
        'rt_user_id_str': [
            (
                obj[rstatus][user][istr]
                if rstatus in obj.keys() else None
            ) for obj in data
        ],
        'rt_status_id_str': [
            (
                obj[rstatus][istr]
                if rstatus in obj.keys() else None
            ) for obj in data
        ],
        'rt_original_date': [
            (
                obj[rstatus]['created_at']
                if rstatus in obj.keys() else None
            ) for obj in data
        ],
        'lang_code': [
            (
                obj[metadata][iso_lang]
                if metadata in obj.keys() else obj[lang]
            ) for obj in data
        ],
        'place_id': [
            (
                obj[place][i] if obj[place] != None else None
            ) for obj in data
        ]
    }

    # quoted screen name
    quoted_user_screen_name = []
    for item in data:
        quoted = None
        if item[isqt] == True and not 'retweeted_status' in item.keys():
            try:
                quoted = item['quoted_status']['user']['screen_name']
            except KeyError:
                quoted = 'NOT AVAILABLE DATA. Quoted tweet was deleted'
                pass
        
        quoted_user_screen_name.append(quoted)
    
    # add quoted screen name to object attrs
    object_attrs['quoted_user_screen_name'] = quoted_user_screen_name

    # map keys
    if key in object_attrs.keys():
        return object_attrs[key]
    else:
        return [
            (
                obj[key] if key in obj.keys() else None
            ) for obj in data
        ]

# process fields
def process_fields(key):
    ''' Returns a function which process and modify data based on key
    '''
    obj = {
        'text': clean_text,
        'full_text': clean_text,
        'source': get_tweet_source,
        'user_id': to_string,
        'in_reply_to_status_id': to_string,
        'in_reply_to_user_id': to_string,
        'quoted_status_id': to_string
    }
    for k, function in obj.items():
        if key == k:
            return function
    
    return False

# process raw data
def get_tweet_data(raw_data, timezone, search_request, endpoint):
    ''' Reads raw data and extracts tweet attrs
    '''
    k = 'tweet'
    db_keys = database_tweet_keys(key=k)

    # main dict
    main = {}
    for key in db_keys:
        attr = process_queries(raw_data, key)
        main[key] = attr
        function = process_fields(key)
        if function:
            main[key] = function(main[key])
    
    # build dataframe
    data = pd.DataFrame(main)
    data['counter'] = 1

    # process created at -> tweet created at
    data = timestamp_attrs(data, timezone)

    # process created at -> if retweet, get original date
    data = timestamp_attrs(data, timezone, col='rt_original_date')

    # tokenized document
    data['tokenized_sentence'] = [
        bag_of_words(document, iso_lang) for document, iso_lang in zip(
            data['full_text'], data['lang_code']
        )
    ]

    # Adding search request
    data['search_request'] = search_request
    data['endpoint_type'] = endpoint

    # replace null values by None
    data = data.where((pd.notnull(data)), None)

    # order columns
    order = order_columns_to_sql(k)
    return data[order].copy()

# insert tweet data
def insert_tweet_data(db_connection, cursor, raw_data, timezone,
    search_request, endpoint):
    ''' Inserts tweet attrs into <tweet> table
    '''
    data = get_tweet_data(
        raw_data, timezone, search_request, endpoint
    )
    sql = """
    INSERT INTO tweet(
        'id', 'id_str', 'created_at_timestamp', 'created_at', 'created_at_year',
        'created_at_month', 'created_at_day', 'created_at_weekday',
        'created_at_month_name', 'created_at_day_name', 'created_at_time_hour',
        'created_at_hour', 'created_at_minute', 'created_at_second',
        'created_at_quarter', 'created_at_dayofyear', 'created_at_weekofyear',
        'text', 'full_text', 'tokenized_sentence', 'retweet_count',
        'favorite_count', 'screen_name', 'user_id', 'user_id_str', 'source',
        'in_reply_to_status_id', 'in_reply_to_status_id_str',
        'in_reply_to_user_id', 'in_reply_to_user_id_str',
        'in_reply_to_screen_name', 'is_quote_status', 'quoted_status_id_str',
        'quoted_user_screen_name', 'is_retweet_status', 'rt_user_screen_name',
        'rt_user_id_str', 'rt_status_id_str', 'rt_original_date_timestamp',
        'rt_original_date', 'rt_original_date_year', 'rt_original_date_month',
        'rt_original_date_day', 'rt_original_date_weekday',
        'rt_original_date_month_name', 'rt_original_date_day_name',
        'rt_original_date_time_hour', 'rt_original_date_hour',
        'rt_original_date_minute', 'rt_original_date_second',
        'rt_original_date_quarter', 'rt_original_date_dayofyear',
        'rt_original_date_weekofyear', 'lang_code', 'place_id', 'counter',
        'search_request', 'endpoint_type'
    ) VALUES(
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
        ?, ?, ?, ?, ?, ?, ?, ?
    )
    ON CONFLICT (id) DO
    UPDATE SET
    retweet_count = EXCLUDED.retweet_count,
    favorite_count = EXCLUDED.favorite_count
    """
    cursor.executemany(sql, tuple(data.values.tolist()))
    db_connection.commit()
    
    return

