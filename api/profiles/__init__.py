# -*- coding: utf-8 -*-

# import modules
from urllib.error import HTTPError
from twitter import *
import time

# import local modules
from utils import nl, twitter_auth, get_max_id
from storage import insert_data

#############################
#                           #
#   Creating API functions  #
#                           #
#############################

# profile data -> Collects user timeline
def profile_data(cnx, **kwargs):
    ''' Downloads user timeline data
    '''
    # store data & default variables
    data = []

    # remove non-endpoint parameters (timezone)
    filtering_keys = ['timezone']
    args = {
        k:v for k, v in kwargs.items() if k not in filtering_keys
    }

    # download data
    try:
        statuses = cnx.statuses.user_timeline(**args)
        if len(statuses) > 0:
            data.extend(statuses)

            # get max id
            max_id = get_max_id(statuses)

            # download more data
            while len(statuses) > 0:
                args['max_id'] = max_id
                statuses = cnx.statuses.user_timeline(**args)
                if len(statuses) > 0:
                    data.extend(statuses)
                    max_id = get_max_id(statuses)
    except TwitterHTTPError:
        pass

    return data

def profile_api(db_connection, cursor, **kwargs):
    ''' Downloads user timeline. Data up to 3,200 posts.
    '''
    # create connection
    cnx = twitter_auth()

    # get data
    data = profile_data(cnx, **kwargs)
    if data:
        # insert data into db file
        insert_data(
            db_connection,
            cursor,
            data,
            kwargs['timezone']
        )
    else:
        nl()
        message = '''
        No data available. Search did not return tweets.
        '''
        print (' '.join(message.split()).lstrip())

    return cnx
