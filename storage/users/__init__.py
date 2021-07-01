# -*- coding: utf-8 -*-

''' Stores users data in <users> table
'''

# import modules
import json
import pandas as pd

# import local modules
from utils import image_url_data, clean_text, convert_to_int, timestamp_attrs

# import database keys
from assets import database_tweet_keys, order_columns_to_sql

# creating functions
def process_queries(data, key):
    ''' Creates a list comprehesion based on data and key
    '''
    # main key
    user = 'user'
    return [
        (obj[user][key] if key in obj[user].keys() else None)
        for obj in data
    ]

# process fields
def process_fields(key):
    ''' Returns a function which process and modify data based on key
    '''
    obj = {
        'profile_image_url_https': image_url_data,
        'description': clean_text,
        'protected': convert_to_int,
        'verified': convert_to_int,
        'location': clean_text,
        'name': clean_text
    }
    for k, function in obj.items():
        if key == k:
            return function

    return False

# process raw data
def get_tweet_data(raw_data, timezone):
    ''' Reads raw data and extracts attrs from users
    '''
    k = 'users'
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

    # Timestamp attrs
    data = timestamp_attrs(data, timezone)
    data = data.where((pd.notnull(data)), None)

    # order columns
    order = order_columns_to_sql(k)
    return data[order].copy()

# insert users data
def insert_users_data(db_connection, cursor, raw_data, timezone):
    ''' Inserts user attrs into <users> table.
    '''
    data = get_tweet_data(raw_data, timezone)
    sql = """
    INSERT INTO users(
        "id", "id_str", "screen_name", "name", 
        "created_at_timestamp", "created_at", "created_at_year",
        "created_at_month", "created_at_day", "created_at_weekday",
        "created_at_month_name", "created_at_day_name",
        "created_at_time_hour", "created_at_hour",
        "created_at_minute", "created_at_second",
        "created_at_quarter", "created_at_dayofyear",
        "created_at_weekofyear", "description", "statuses_count",
        "protected", "verified", "followers_count",
        "favourites_count", "friends_count", "listed_count",
        "location", "profile_image_url_https", "url"
    ) VALUES(
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
        ?, ?, ?, ?, ?
    )
    ON CONFLICT (id, screen_name) DO
    UPDATE SET
    description = EXCLUDED.description,
    name = EXCLUDED.name,
    statuses_count = EXCLUDED.statuses_count,
    protected = EXCLUDED.protected,
    verified = EXCLUDED.verified,
    followers_count = EXCLUDED.followers_count,
    favourites_count = EXCLUDED.favourites_count,
    friends_count = EXCLUDED.friends_count,
    listed_count = EXCLUDED.listed_count,
    location = EXCLUDED.location,
    profile_image_url_https = EXCLUDED.profile_image_url_https,
    url = EXCLUDED.url
    """
    cursor.executemany(sql, tuple(data.values.tolist()))
    db_connection.commit()

    return
