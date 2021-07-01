# -*- coding: utf-8 -*-

# import modules
from twitter import *
import time

# Exceptions
from urllib.error import HTTPError

# import local modules
from utils import nl, twitter_auth, get_max_id, sleep_application
from storage import insert_data

#############################
#                           #
#   Creating API functions  #
#                           #
#############################

# keyword data -> Collects first batch of data
def keyword_data(cnx, **kwargs):
    ''' Downloading data from API
    '''
    # store data & default variables
    data = []
    last_max_id = 1
    exceed_api_limit = False

    # remove non-endpoint parameters (timezone)
    filtering_keys = ['timezone']
    args = {
        k:v for k, v in kwargs.items() if k not in filtering_keys
    }

    # create request
    statuses = cnx.search.tweets(**args)
    tweets = statuses['statuses']
    if len(tweets) > 0:
        data.extend(tweets)
        max_id = get_max_id(data)

        # download attrs
        last_max_id = f'{max_id}'

        # download more data
        try:
            while len(statuses) > 0:
                args['max_id'] = max_id
                statuses = cnx.search.tweets(**args)
                tweets = statuses['statuses']
                if len(tweets) > 0:
                    max_id = get_max_id(tweets)
                    last_max_id = f'{max_id}'
                    data.extend(tweets)
                else:
                    break
        except (TwitterHTTPError, HTTPError):
            exceed_api_limit = True
            pass

    return data, last_max_id, exceed_api_limit

# download more tweets
def update_kw_data_backwards(cnx, max_id, **kwargs):
    ''' Download data backwards based on max_id (oldest tweet downloaded)
    in a set of tweets.

    Function will run if available data is higher than ~18,000 tweets approximately.
    '''
    # store data
    data = []

    # filter kwargs and get endpoint's arguments
    filtering_keys = ['timezone']
    args = {
        k:v for k, v in kwargs.items() if k not in filtering_keys
    }

    # add max id value
    args['max_id'] = max_id

    update = True
    while update:
        try:
            statuses = cnx.search.tweets(**args)
            update = False
        except (TwitterHTTPError, HTTPError):
            # sleeping -> type of query => keyword
            remain, reset = sleep_application(cnx, 'keyword')
            if remain <= 10:
                sleep_for = int(reset - time.time()) + 10
                time.sleep(sleep_for)
            
            continue
    
    # extract statuses
    tweets = statuses['statuses']
    if not tweets:
        return False
    else:
        data.extend(tweets)
        max_id = get_max_id(tweets)

        last_max_id = f'{max_id}'
        try:
            while len(statuses) > 0:
                args['max_id'] = max_id
                statuses = cnx.search.tweets(**args)
                tweets = statuses['statuses']
                if len(tweets) > 0:
                    max_id = get_max_id(tweets)
                    last_max_id = f'{max_id}'
                    data.extend(tweets)
                else:
                    break
        except TwitterHTTPError:
            pass

        response = (data, last_max_id)
        return response

# Keyword API
def keyword_api(db_connection, cursor, **kwargs):
    ''' The Twitter Search API searches against a sampling of recent Tweets
    published in the past 7 days.

    '''
    # create twitter api connection
    cnx = twitter_auth()

    # get data
    data, last_max_id, exceed_api_limit = keyword_data(cnx, **kwargs)
    if data:
        # insert first batch of data to .db file
        nl()
        insert_data(
            db_connection,
            cursor,
            data,
            kwargs['timezone']
        )

        # explore requests limits - type of query => keyword
        remain, reset = sleep_application(cnx, 'keyword')
        if exceed_api_limit:
            # sleeping
            sleep_for = int(reset - time.time()) + 10
            time.sleep(sleep_for)

            '''
            Apply function update_kw_data_backwards.
            Function will start to download more historical data of recent Tweets
            published in the past 7 days.
            '''
            while True:
                res = update_kw_data_backwards(cnx, last_max_id, **kwargs)
                if res != False:
                    data, last_max_id = res
                    
                    # insert data to .db file
                    insert_data(
                        db_connection,
                        cursor,
                        data,
                        kwargs['timezone']
                    )

                    # sleeping -> type of query => keyword
                    remain, reset = sleep_application(cnx, 'keyword')
                    if remain <= 10:
                        sleep_for = int(reset - time.time()) + 10
                        time.sleep(sleep_for)
                    
                    continue
                else:
                    break
    else:
        nl()
        message = '''
        No data available. Search did not return tweets.
        '''
        print (' '.join(message.split()).lstrip())
    
    return cnx

