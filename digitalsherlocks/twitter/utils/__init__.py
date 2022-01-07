# -*- coding: utf-8 -*-

''' This file compiles a set of functions

Collects parameters from user
Loads Twitter API credentials and connects to API
Creates a .db file using sqlite3
Collects and process attrs from Twitter data
Builds and saves a network-like dataset
'''

# import modules
from w3lib.html import replace_entities
from bs4 import BeautifulSoup as bs
from twitter import *
import pandas as pd
import sqlite3
import time
import re
import os

# Exceptions
from pytz.exceptions import UnknownTimeZoneError

# local modules
from assets import stopwords

# new line
def nl():
    print ('')


# search tweets parameters
def search_tweets_params(update):
    '''
    Defines search tweets parameters
    '''
    geocode = '[Optional] Geocode format -> latitude,longitude,radius: '
    parameters = {
        'q': input('[Required] query: '),
        'lang': input('[Optional] language: '),
        'result_type': input('[Required] Result type -> Options [mixed, recent, popular]: '),
        'timezone': input('[Required] Timezone: '),
        'geocode': input(geocode),
        'since_id': '1' if update == False else int(input('Since ID: ')),
        'tweet_mode': 'extended',
        'count': 100
    }

    return parameters


# user timeline parameters
def user_timeline_params(update):
    ''' Defines user timeline parameters
    '''
    exclude_replies = '[Required] Exlude replies -> Options [1, 0]: '
    include_rts = '[Required] Include Retweets -> Options [1, 0]: '
    parameters = {
        'screen_name': input('[Required] Username: '),
        'exclude_replies': input(exclude_replies),
        'include_rts': input(include_rts),
        'timezone': input('[Required] Timezone: '),
        'since_id': '1' if update == False else int(input('Since ID: ')),
        'tweet_mode': 'extended',
        'count': 200
    }

    return parameters

# collect parameters from user
def collect_parameters():
    '''
    A set of inputs to collect data from users

    - Attrs will be used to create the parameters needed for the Twitter API
    '''
    print ('Select request type.')
    print ('Type 1 for Search tweets.')
    print ('Type 2 for User timeline.')
    print ('Type 3 for User connections (followers or friends).')
    
    request_type = input('> ')
    opts = {
        '1': 'Search tweets',
        '2': 'User timeline',
        '3': 'User connections'
    }

    while True:
        try:
            req_type_opt = opts[request_type]
            break
        except KeyError:
            nl()
            print ('Not a correct option. Try again.')
            request_type = input('> ')
            continue

    if request_type in ['1', '2']:
        # verify if user will update a database
        nl()
        print ('Are you going to update a database?')
        print ('Type 0 for False.')
        print ('Type 1 for True.')
        update_status = bool(int(' '.join(input('> ').split())))

        # new line
        nl()

        # config parameters
        if req_type_opt == 'Search tweets':
            parameters = search_tweets_params(update_status)
            parameters['result_type'] = parameters['result_type'] \
                if parameters['result_type'] in ['mixed', 'recent', 'popular'] \
                    else 'mixed'
        else:
            parameters = user_timeline_params(update_status)

            parameters['exclude_replies'] = parameters['exclude_replies'] \
                if parameters['exclude_replies'] in ['1', '0'] else '1'
            
            parameters['include_rts'] = parameters['include_rts'] \
                if parameters['include_rts'] in ['1', '0'] else '0'
        
        if req_type_opt == 'Search tweets':
            parameters['q'] = ' '.join(parameters['q'].split())
            parameters['result_type'] = ' '.join(
                parameters['result_type'].lower().split()
            )
            parameters['timezone'] = ' '.join(parameters['timezone'].split())
            parameters['lang'] = ' '.join(parameters['lang'].lower().split()) \
                if parameters['lang'] != '' else None
            parameters['geocode'] = ' '.join(parameters['geocode'].lower().split()) \
                if parameters['geocode'] != '' else None
            
            # removing keys from None values in optional parameters
            for k in ['geocode', 'lang']:
                if parameters[k] == None:
                    del parameters[k]

            # compile parameters in tuple
            res = ('keyword', parameters)
        else:
            parameters['screen_name'] = ' '.join(parameters['screen_name'].split())
            parameters['timezone'] = ' '.join(parameters['timezone'].split())
            parameters['exclude_replies'] = bool(int(' '.join(
                parameters['exclude_replies'].split()
            )))
            parameters['include_rts'] = bool(int(' '.join(
                parameters['include_rts'].split()
            )))

            # compile parameters in tuple
            res = ('profile', parameters)
    else:
        # new line
        nl()
        nl()
        print ('Type 1 for Followers.')
        print ('Type 2 for Friends.')
        method = ' '.join(input('> ').split())

        user_connection_opts = {
            '1': 'followers',
            '2': 'friends'
        }

        # get parameters
        nl()
        parameters = {
            'method': user_connection_opts[method],
            'screen_name': input('[Required] Username: '),
        }

        res = ('user_connections', parameters)

    # parameters
    return res


# creates database
def create_db_file(folder, sqlpath):
    '''
    '''
    if folder.endswith('/'):
        folder = folder[:-1]
    
    folder = f'{folder}/data/'
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
    
    # create db file
    path = f'{folder}data.db'
    conn = sqlite3.connect(path)

    # get cursor
    cursor = conn.cursor()

    # encoding databse
    cursor.execute('PRAGMA encoding')

    # reading sql file
    sql_file = open(sqlpath)
    reader = sql_file.read()

    # execute script
    cursor.executescript(reader)

    # commit created tables
    conn.commit()
    
    return conn, cursor


# load credentials
def load_credentials():
    '''
    Loads Twitter API credentials
    '''
    return {
        'token': '',
        'token_secret': '',
        'consumer_key': '',
        'consumer_secret': ''
    }


# twitter authentication
def twitter_auth():
    '''
    Twitter authentication
    '''
    credentials = load_credentials()

    # credentials
    tkn = credentials['token']
    tkn_secret = credentials['token_secret']
    consumer_k = credentials['consumer_key']
    consumer_secret = credentials['consumer_secret']

    # authenticate
    Auth = OAuth(tkn, tkn_secret, consumer_k, consumer_secret)
    return Twitter(auth=Auth)


'''
Collecting attrs from Twitter data
'''
def timestamp_attrs(data, timezone, col='created_at'):
    '''
    '''
    try:
        t = pd.to_datetime(
            data[col],
            utc=True,
            infer_datetime_format=True
        ).apply(lambda x: x.tz_convert(timezone))
    except UnknownTimeZoneError:
        timezone = 'Universal'
        t = pd.to_datetime(
            data[col],
            utc=True,
            infer_datetime_format=True
        ).apply(lambda x: x.tz_convert(timezone))

    # timestamp sttributes
    data[f'{col}_timestamp'] = t.dt.strftime('%Y-%m-%d %H:%M:%S')
    data[f'{col}'] = t.dt.strftime('%Y-%m-%d')
    data[f'{col}_year'] = t.dt.year
    data[f'{col}_month'] = t.dt.month
    data[f'{col}_day'] = t.dt.day
    data[f'{col}_weekday'] = t.dt.dayofweek
    data[f'{col}_month_name'] = t.dt.month_name()
    data[f'{col}_day_name'] = t.dt.day_name()
    data[f'{col}_time_hour'] = t.dt.strftime('%H:%M:%S')
    data[f'{col}_hour'] = t.dt.hour
    data[f'{col}_minute'] = t.dt.minute
    data[f'{col}_second'] = t.dt.second
    data[f'{col}_quarter'] = t.dt.quarter
    data[f'{col}_dayofyear'] = t.dt.dayofyear
    data[f'{col}_weekofyear'] = [
        (i.isocalendar()[1] if str(i) != 'NaT' else None) for i in t
    ]

    return data

def get_max_id(data):
    ''' Get max id in a set of tweets -> oldest tweet downloaded
    '''
    return min([i['id'] for i in data]) - 1

def image_url(url):
	''' Splits img url to get the best size of the image
	'''
	u = url.split('_normal')
	if len(u) > 1:
		return f'{u[0]}{u[-1]}'
	else:
		return url

def image_url_data(data):
	''' Applies function to each item in data
	'''
	return [image_url(url) for url in data]

def clean_text(data):
    ''' Cleans text, removing blackspaces, tabs, new lines, etc
    '''
    documents = [
        ' '.join(
            txt.replace('\x00', '').split()
        ).strip() for txt in data
    ]

    return [replace_entities(txt) for txt in documents]

def convert_to_int(data):
	''' Converts boolean values into integers (1, 0)
	'''
	return [int(boolean) for boolean in data]

def to_string(data):
	''' Converts items in list into string
	'''
	return [(str(i) if i != None else i) for i in data]

def get_anchor_text(html):
	''' Reads html source and returns text inside tags
	'''
	try:
		src = bs(html, 'lxml')
	except:
		src = bs(html, 'html5lib')
		
	return src.text

def get_tweet_source(data):
	''' Uses get_anchor_text function to extract tweet source
	'''
	return [get_anchor_text(html) for html in data]


# process tweet text
def load_stopwords(iso_lang):
    '''
    '''
    return stopwords(iso_lang)

def remove_punctuation(document):
    ''' Removes punctuation from tweet
    '''
    pattern = re.compile(r'(\w+)')
    tokenized = [i.group() for i in pattern.finditer(document)]
    
    # return clean document without punctuation 
    return ' '.join(tokenized).strip()

def bag_of_words(document, iso_lang):
    ''' Tokenizes text
    '''
    # clean text
    document = ' '.join([i for i in document.split() if not i.startswith('http')])
    document = ' '.join(document.split()).strip().lower()
    
    # remove punctuation from document
    document = remove_punctuation(document)
    split_document = document.split()

    # load stop words
    if iso_lang:
        stop_words_asset = load_stopwords(iso_lang)
        split_document = [
            i for i in split_document if i not in stop_words_asset
        ]

    return ' '.join(split_document).strip()

# sleep application
def sleep_application(api_connection, type_of_query):
    ''' Checks the number of requests and returns the remaining and reset values
    from twitter api limits
    '''
    rate_limit_status = api_connection.application.rate_limit_status()
    if type_of_query == 'keyword':
        target = '/search/tweets'
        rls = rate_limit_status['resources']['search'][target]
    else:
        target = '/statuses/user_timeline'
        rls = rate_limit_status['resources']['statuses'][target]
    
    return rls['remaining'], rls['reset']

'''
Processing data to build a network-like dataset
'''

# clean screen name
def clean_screen_name(user):
    ''' Removes @ in handle and transform screen name into lowercase
    '''
    if type(user) != list:
        if user.startswith('@'):
            user = user[1:]
        
        return user.lower()
    else:
        return [
            (i[1:].lower() if i.startswith('@') else i.lower())
            for i in user
        ]

# write record
def write_record(record, target, connection_type, row, output):
    ''' Writes dataframe record in the edges file
    '''
    # get attrs
    source = clean_screen_name(record['screen_name'])
    target = clean_screen_name(target)
    software = record['source']
    tweet_id = record['id_str']
    if source != target:
        date = str(record['created_at_timestamp'])
        if type(connection_type) != list:
            connection_type = [connection_type]
        
        # build temp dict
        temp = {
            'source': source,
            'target': target,
            'connection_type': connection_type,
            'software': software,
            'sequence': row,
            'date': date,
            'timestamp': int(
                pd.to_datetime(
                    date, yearfirst=True
                ).timestamp()
            ),
            'tweet_id': tweet_id
        }

        # write record
        df = pd.DataFrame(temp)
        df.to_csv(
            output,
            mode='a',
            index=False,
            header=False,
            encoding='utf-8'
        )
    
    return

# get mentions in tweet
def get_mentions(text):
    '''
    '''

    return [i for i in re.findall(r'@(\w+)', text)]

# eval mentions
def evalmentions(record, row, output):
    '''
    '''
    text = record['full_text']
    mentions = get_mentions(text)
    if len(mentions) > 0:
        # process record
        text = text.replace('\x00', '')
        tokens = ' '.join(text.split()).strip().split()
        thread_reply = []
        mentioned_users = []

        # find reply
        reply = 1 if record['in_reply_to_status_id'] != None else 0
        if reply:
            for i in tokens:
                i = i.strip()
                if i.startswith('@'):
                    # append i < user > and remove @ -> i[1:]
                    thread_reply.append(i[1:])
                else:
                    '''

                    stop iteration. this assumes that
                    there are no more mentions in thread
                    '''
                    break
            
        # eval number of mentions
        if len(mentions) == len(thread_reply):
            target = thread_reply
            cnx_type = ['reply'] * len(thread_reply)

            # write record
            write_record(record, target, cnx_type, row, output)
        else:
            mentioned_users = [
                i for i in mentions if i not in thread_reply
            ]

            # build target
            target = thread_reply + mentioned_users
            
            # build cnx_type
            cnx_type = ['reply'] * len(thread_reply) + \
                ['mention'] * len(mentioned_users)
            
            # write records
            write_record(record, target, cnx_type, row, output)

    return
