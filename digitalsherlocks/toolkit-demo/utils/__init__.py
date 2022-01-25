# -*- coding: utf-8 -*-

# =========================================
# digitalsherlocks
# A DFRLab project
#
# Author: @estebanpdl
#
# File: Utils.
# =========================================

# import modules
import pandas as pd
import sqlite3
import time
import re
import os


# new line
def nl():
    print ('')


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