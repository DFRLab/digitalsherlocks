# -*- coding: utf-8 -*-

# =========================================
# digitalsherlocks
# A DFRLab project
#
# Author: @estebanpdl
#
# File: main script.
# =========================================


'''

CLI main file

'''

# Import logs modules
from colorama import Style, Fore
from colorama import init as COLORAMA_INIT
COLORAMA_INIT()

# welcome Message
from pyfiglet import Figlet
font = Figlet(font='big')
message = '''
    digitalsherlocks
'''
print (Style.BRIGHT + font.renderText(message))
print ('''
              ===================================================
''')
print ('')
print (Fore.RESET)


'''

Import modules
'''
import sys
import shutil

# import from modules
from logs import printl
from argparse import (
    ArgumentParser, RawTextHelpFormatter
)

from arguments import ProcessArguments
from arguments.utils import (
    aligntext
)

# main function
def main():
    '''

    main function
    '''
    
    # creating argument parser
    parser = ArgumentParser(
        prog='digitalsherlocks'
    )

    # adding subparser
    subparser = parser.add_subparsers(
        title='Command line interface [cli]',
        description='',
        metavar='subcommand'
    )

    # creating CLI parser
    cli = subparser.add_parser(
        'cli',
        description='''
        Allows using tool through the command line
        ==========================================
        ''',
        help='Allows using digitalsherlocks through the command line.'
    )

    '''

    CLI Argument < working directory >
    '''
    cli.add_argument(
        '-wd',
        '--working-dir',
        type=str,
        help='Specifies an optional working directory.',
        metavar='WORKPATH',
        dest='wd'
    )

    '''

    CLI Arguments < subparsers >
    '''
    cli_args = cli.add_subparsers(
        title='CLI Arguments',
        description='',
        dest='service',
        metavar='subcommand'
    )


    '''

    CLI Arguments: Twitter
    '''
    twitter = cli_args.add_parser(
        'twitter',
        description='''
        Connects to Twitter API using user authentication
        =================================================
        ''',
        help='Connects to Twitter API using user authentication.'
    )

    
    '''

    Twitter database-related arguments
    '''

    # update an existing database
    twitter.add_argument(
        '--update-database',
        help='Confirms if an existing database needs to be updated.',
        action='store_true',
        default=False,
        dest='update_database'
    )
    
    # database name
    twitter.add_argument(
        '--db-path',
        type=str,
        help='Reads an existing database or creates a new database using this path.',
        metavar='FILE.db',
        dest='dbpath',
        required='--update-database' in sys.argv
    )

    # update an exiting database using db attrs [previous searches]
    twitter.add_argument(
        '--using-db-attrs',
        help='Updates database using previous searches only.',
        action='store_true',
        default=False,
        dest='update_db_attrs'
    )

    # custom database name
    twitter.add_argument(
        '--add-db-name',
        type=str,
        help='Creates a custom database name.',
        metavar='NAME',
        dest='dbname'
    )


    '''

    Creating Twitter sub parsers
    '''
    twitter_subparsers = twitter.add_subparsers(
        title='Twitter arguments',
        description='',
        dest='endpoint',
        metavar='subcommand'
    )


    '''

    Twitter: users
    Get user timeline data
    '''
    twitter_users = twitter_subparsers.add_parser(
        'users',
        description='''
        Returns a collection of Tweets posted by the user
        =================================================
        ''',
        help='Returns a collection of Tweets posted by the user.'
    )


    '''

    Twitter: tweets
    Collect data by searching tweets matching a query
    '''

    twitter_tweets = twitter_subparsers.add_parser(
        'tweets',
        description='''
        Returns a collection of Tweets
        ==============================
        ''',
        help='Returns a collection of Tweets matching a query.'
    )


    '''

    Twitter: friendships
    Get followers and friends of one arbitrary user
    '''
    twitter_friendships = twitter_subparsers.add_parser(
        'friendships',
        formatter_class=indent_formatter,
        description='''
        Get followers and friends of one arbitrary user
        ===============================================
        ''',
        help='Returns followers and friends of one arbitrary user.'
    )


    '''

    Twitter argument groups
    '''

    twitter_user_args = twitter_users.add_argument_group(
        'User timelines options',
        description=''
    )

    twitter_tweets_args = twitter_tweets.add_argument_group(
        'Search tweets options',
        description=''
    )

    twitter_friendships_args = twitter_friendships.add_argument_group(
        'Friendships options',
        description=''
    )


    '''

    Twitter: user timelines-related arguments
    '''

    # user name timeline
    twitter_user_args.add_argument(
        '--user-name-timeline',
        type=str,
        help='Returns a collection of the most recent Tweets posted by the user indicated by the screen_name.',
        metavar='NAME',
        dest='screen_name',
        required=not '--user-id-timeline' in sys.argv
    )

    # user id timeline
    twitter_user_args.add_argument(
        '--user-id-timeline',
        type=str,
        help='Returns a collection of the most recent Tweets posted by the user indicated by the user_id.',
        metavar='ID',
        dest='user_id',
        required=not '--user-name-timeline' in sys.argv
    )

    # exclude replies
    twitter_user_args.add_argument(
        '--exclude-replies',
        help='Prevents replies from appearing in the returned timeline. Default: False.',
        action='store_true',
        default=False,
        dest='exclude_replies'
    )

    # include retweets
    twitter_user_args.add_argument(
        '--include-rts',
        help='Includes retweets in the returned timeline. Default: False.',
        action='store_true',
        default=False,
        dest='include_rts'
    )

    # since id
    twitter_user_args.add_argument(
        '--since-id',
        type=str,
        help='Returns results with an ID greater than (that is, more recent than) the specified ID. Default 1.',
        metavar='ID',
        default='1',
        dest='since_id'
    )

    # max id
    twitter_user_args.add_argument(
        '--max-id',
        type=str,
        help='Returns results with an ID less than (that is, older than) or equal to the specified ID.',
        metavar='ID',
        dest='max_id'
    )

    # count < number of tweets per request >
    twitter_user_args.add_argument(
        '--count',
        type=int,
        help='Number of tweets to return per request. Max 200. Default 200.',
        metavar='NUMBER',
        default=200,
        dest='count'
    )

    # timezone
    twitter_user_args.add_argument(
        '-tz',
        '--timezone',
        type=str,
        help='Converts UTC data from posts into specified timezone. Default Universal.',
        metavar='TIMEZONE',
        default='Universal',
        dest='timezone'
    )


    '''

    Twitter: search tweets-related arguments
    '''

    # query
    twitter_tweets_args.add_argument(
        '-q',
        '--query',
        type=str,
        help='A search query of 500 characters maximum, including operators.',
        metavar='QUERY',
        dest='q',
        required=True
    )

    # language
    twitter_tweets_args.add_argument(
        '-l',
        '--language',
        type=str,
        help=aligntext('''Restricts tweets to the given language,
        given by an ISO 639-1 code.
        '''),
        metavar='LANGUAGE',
        dest='lang'
    )

    # result type
    twitter_tweets_args.add_argument(
        '--result-type',
        type=str,
        choices=['popular', 'mixed', 'recent'],
        help='Specifies type of search results. Options: mixed, popular, recent. Default mixed.',
        metavar='TYPE',
        default='mixed',
        dest='result_type'
    )

    # count < number of tweets per request >
    twitter_tweets_args.add_argument(
        '--count',
        type=int,
        help='Number of tweets to return per request. Max 100. Default 100.',
        metavar='NUMBER',
        default=100,
        dest='count'
    )

    # until
    twitter_tweets_args.add_argument(
        '--until',
        type=str,
        help='Returns tweets created before the given date.',
        metavar='DATE',
        dest='until'
    )

    # since id
    twitter_tweets_args.add_argument(
        '--since-id',
        type=str,
        help='Returns results with an ID greater than (that is, more recent than) the specified ID. Default 1.',
        metavar='ID',
        default='1',
        dest='since_id'
    )

    # max id
    twitter_tweets_args.add_argument(
        '--max-id',
        type=str,
        help='Returns results with an ID less than (that is, older than) or equal to the specified ID.',
        metavar='ID',
        dest='max_id'
    )

    # timezone
    twitter_tweets_args.add_argument(
        '-tz',
        '--timezone',
        type=str,
        help='Converts UTC data from posts into specified timezone. Default Universal.',
        metavar='TIMEZONE',
        default='Universal',
        dest='timezone'
    )

    
    '''

    Twitter: friendships-related arguments
    '''
    twitter_friendships_args.add_argument(
        '--type',
        type=str,
        choices=['followers', 'friends'],
        help='Type of friendship. Options: followers, friends.',
        dest='friendship_type',
        required=True
    )

     # by username
    twitter_friendships_args.add_argument(
        '--user-name',
        type=str,
        help='Screen name of the user for whom to return results.',
        metavar='NAME',
        dest='screen_name',
        required=not '--user-id' in sys.argv
    )

    # by userid
    twitter_friendships_args.add_argument(
        '--user-id',
        type=str,
        help='The ID of the user for whom to return results',
        metavar='ID',
        dest='user_id',
        required=not '--user-name' in sys.argv
    )

    twitter_friendships_args.add_argument(
        '--cursor',
        type=int,
        help='Causes the list of connections to be broken into pages of no more than 5000 IDs at a time. Default -1',
        metavar='CURSOR',
        default=-1,
        dest='cursor'
    )

    # count < number of results to return >
    twitter_friendships_args.add_argument(
        '--count',
        type=int,
        help='Specifies the number of IDs attempt retrieval of. Max 5,000 per distinct request. Default 5,000.',
        metavar='NUMBER',
        default=5000,
        dest='count'
    )

    '''

    Get arguments
    '''
    args = vars(parser.parse_args())


    # Logs
    printl('Welcome', color='CYAN')
    printl('Program started', color='GREEN')
    printl('Collecting arguments')

    '''

    Process arguments
    '''
    kwarg_handler = ProcessArguments(args)
    
    
    # get data
    kwarg_handler.connect_service()


# execute
if __name__ == '__main__':
    '''

    run main function
    '''
    main()
