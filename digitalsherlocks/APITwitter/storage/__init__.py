# -*- coding: utf-8 -*-

''' Stores data in db file
'''

# import storage local modules
from APITwitter.storage.media_tweet import insert_media_tweet_data
from APITwitter.storage.media_video import insert_media_video_data
from APITwitter.storage.mentions import insert_mentions_data
from APITwitter.storage.hashtags import insert_hashtags_data
from APITwitter.storage.users import insert_users_data
from APITwitter.storage.place import insert_place_data
from APITwitter.storage.tweet import insert_tweet_data
from APITwitter.storage.media import insert_media_data
from APITwitter.storage.urls import insert_urls_data

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
