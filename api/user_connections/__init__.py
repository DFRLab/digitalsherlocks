# -*- coding: utf-8 -*-

# import modules
from urllib.error import HTTPError
from twitter import *
import time

# import local modules
from utils import nl, twitter_auth
from store_user_connections import insert_users_data

# get connections
def get_connections(cnx, db_connection, cursor, screen_name, method):
    '''
    '''
    # build params
    params = {
        'screen_name': screen_name,
        'cursor': -1,
        'count': 5000,
        'stringify_ids': True
    }

    # API call target
    t = f'/{method}/ids'

    # application status
    app_status = cnx.application.rate_limit_status()
    if app_status['resources'][method][t]['remaining'] <= 0:
        sleep_until = app_status['resources'][method][t]['reset']
        sleep_for = int(sleep_until - time.time()) + 10
        time.sleep(sleep_for)
    
    if method == 'followers':
        users = cnx.followers.ids(**params)
    else:
        users = cnx.friends.ids(**params)

    # store ids in table
    data = [tuple([i]) for i in users['ids']]
    sql = """
    INSERT INTO ids(
        "id_str"
    ) VALUES(
        ?
    )
    """
    cursor.executemany(sql, data)
    db_connection.commit()

    # get next cursor
    api_cursor = users['next_cursor']
    while api_cursor != 0:
        params['cursor'] = api_cursor
        try:
            if method == 'followers':
                users = cnx.followers.ids(**params)
            else:
                users = cnx.friends.ids(**params)
            
            '''
            Save user ids
            '''

            data = [tuple([i]) for i in users['ids']]
            sql = """
            INSERT INTO ids(
                "id_str"
            ) VALUES(
                ?
            )
            """
            cursor.executemany(sql, data)
            db_connection.commit()

            # get next cursor
            api_cursor = users['next_cursor']
        except (TwitterHTTPError, HTTPError):
            app_status = cnx.application.rate_limit_status()
            if app_status['resources'][method][t]['remaining'] <= 0:
                sleep_until = app_status['resources'][method][t]['reset']
                sleep_for = int(sleep_until - time.time()) + 10
                time.sleep(sleep_for)
            
            continue
    
    return

def user_connection(db_connection, cursor, **kwargs):
    '''
    '''
    # create connection
    cnx = twitter_auth()

    # get ids
    screen_name = kwargs['screen_name']
    method = kwargs['method']
    get_connections(
        cnx,
        db_connection,
        cursor,
        screen_name,
        method
    )

    # get ids
    sql = """
    SELECT *
    FROM ids
    """
    cursor.execute(sql)

    # get data
    data = [j for i in cursor.fetchall() for j in i]
    batch = 100
    ids = [data[i: i + batch] for i in range(0, len(data), batch)]

    # check rate limits
    status = cnx.application.rate_limit_status()
    lookup_remaining_calls = status['resources']['users']['/users/lookup']['remaining']
    for accounts in ids:
        '''
        Verify cnx status
        '''
        if lookup_remaining_calls == 50:
            status = cnx.application.rate_limit_status()
            lookup_remaining_calls = status['resources']['users']['/users/lookup']['remaining']
        if lookup_remaining_calls <= 0:
            sleep_until = status['resources']['users']['/users/lookup']['reset']
            sleep_for = int(sleep_until - time.time()) + 10
            if sleep_for > 0:
                time.sleep(sleep_for)
                status = cnx.application.rate_limit_status()
                lookup_remaining_calls = status['resources']['users']['/users/lookup']['remaining']
            
        lookup_remaining_calls -= 1

        # user lookup data
        raw_data = cnx.users.lookup(user_id=','.join(accounts))
        insert_users_data(
            db_connection,
            cursor,
            raw_data
        )

    return