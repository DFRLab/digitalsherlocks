# -*- coding: utf-8 -*-

''' Stores data in db file
'''

# import storage local modules
from storage.media_tweet import insert_media_tweet_data
from storage.media_video import insert_media_video_data
from storage.mentions import insert_mentions_data
from storage.hashtags import insert_hashtags_data
from storage.users import insert_users_data
from storage.place import insert_place_data
from storage.tweet import insert_tweet_data
from storage.media import insert_media_data
from storage.urls import insert_urls_data

# main function -> insert data
def insert_data(db_connection, cursor, raw_data, timezone):
    '''
    '''
    # users
    insert_users_data(db_connection, cursor, raw_data, timezone)

    # tweet
    insert_tweet_data(db_connection, cursor, raw_data, timezone)

    # media tweet
    insert_media_tweet_data(db_connection, cursor, raw_data)

    # media video
    insert_media_video_data(db_connection, cursor, raw_data)

    # mentions
    insert_mentions_data(db_connection, cursor, raw_data)

    # hashtags
    insert_hashtags_data(db_connection, cursor, raw_data)

    # media
    insert_media_data(db_connection, cursor, raw_data)

    # place
    insert_place_data(db_connection, cursor, raw_data)

    # urls
    insert_urls_data(db_connection, cursor, raw_data)

    return
