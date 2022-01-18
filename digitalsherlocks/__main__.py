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

# welcome Message
from pyfiglet import Figlet
font = Figlet(font='big')
message = '''
    Digitalsherlocks
'''
print (font.renderText(message))
print ('')
print ('''
        =============================================================
        =============================================================
''')
print ('')

'''

Import modules
'''
import sys
import shutil
import logging

# import from modules
from argparse import (
    ArgumentParser, RawTextHelpFormatter
)

from arguments import ProcessArguments
from arguments.utils import (
    aligntext
)

# Twitter
from APITwitter import API

# main function
def main():
    '''

    main function
    '''

    # logging config
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.DEBUG
    )

    logging.info('Welcome')
    logging.info('Started')
    
    # creating argument parser
    parser = ArgumentParser(
        prog='digitalsherlocks'
    )
    
    '''

    Text formatter -> RawTextHelpFormatter
    '''
    indent_formatter = lambda prog: RawTextHelpFormatter(
        prog,
        width=shutil.get_terminal_size().columns,
        max_help_position=500
    )

    # adding subparser
    subparser = parser.add_subparsers(
        title='Command line interface [cli]',
        description='',
        metavar='subcommand\n'
    )

    # creating CLI parser
    cli = subparser.add_parser(
        'cli',
        formatter_class=indent_formatter,
        description='''
        Allows using tool through the command line
        ==========================================
        ''',
        help='Allows using digitalsherlocks through the command line.',
        epilog='''
        
        Examples:

        Add a custom working directory.
          $ digitalsherlocks cli -wd path/to/my/folder

        Shows help message
          $ digitalsherlocks cli -h
          $ digitalsherlocks cli twitter -h
        '''.lstrip()
    )

    '''

    CLI Argument < working directory >
    '''
    cli.add_argument(
        '-wd',
        '--working-dir',
        type=str,
        help=aligntext('''Output directory. Specifies an optional
        working directory. Default: current working directory.
        '''),
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
        metavar='subcommand\n'
    )


    '''

    CLI Arguments: Twitter
    '''
    twitter = cli_args.add_parser(
        'twitter',
        formatter_class=indent_formatter,
        description='''
        Connects to Twitter API using user authentication
        =================================================
        ''',
        help='Connects to Twitter API using user authentication.',
        epilog='''

        Examples:

        Create a new database with a custom name
          $ digitalsherlocks cli twitter --add-db-name myresearch

        Update an existing database
          $ digitalsherlocks cli twitter --update-database --db-path path/to/my/file.db

        Shows help message for Twitter API users' endpoint
          $ digitalsherlocks cli twitter users -h
        '''.lstrip()
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
        help=aligntext('''Reads an existing database or creates a new
        database using this path. Argument is
        required, if <update database> is true.
        '''),
        metavar='FILE.db',
        dest='dbpath',
        required='--update-database' in sys.argv
    )

    # custom database name
    twitter.add_argument(
        '--add-db-name',
        type=str,
        help=aligntext('''Creates a custom database name. Default:
        data.db. This argument will not take into account if a
        <db path> or an existing database was added using the
        --db-path argument.
        '''),
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
        metavar='subcommand\n'
    )


    '''

    Twitter: users
    '''
    twitter_users = twitter_subparsers.add_parser(
        'users',
        formatter_class=indent_formatter,
        description='''
        Uses Twitter users-related endpoints
        ====================================
        ''',
        help='Uses Twitter users-related endpoints.',
        epilog='''

        Examples:

        Get user timeline from POTUS (by default, this command will include replies but not retweets)
          $ digitalsherlocks cli twitter users --user-name-timeline POTUS

        Get user timeline from user id 1234567
          $ digitalsherlocks cli twitter users --user-id-timeline 1234567

        Get user timeline from POTUS, including retweets but excluding replies
          $ digitalsherlocks cli twitter users --user-name-timeline POTUS --include-rts --exclude-replies

        Get user timeline from POTUS, including both retweets and replies
          $ digitalsherlocks cli twitter users --user-name-timeline POTUS --include-rts
        '''.lstrip()
    )

    twitter_user_args = twitter_users.add_argument_group(
        'Twitter API users options',
        description=''
    )

    
    '''

    Twitter: users timeline-related arguments
    '''

    # user name timeline
    twitter_user_args.add_argument(
        '--user-name-timeline',
        type=str,
        help=aligntext('''Returns a collection of the most recent
        Tweets posted by the user indicated by the screen_name.
        '''),
        metavar='handlename',
        dest='screen_name',
        required=not '--user-id-timeline' in sys.argv
    )

    # user id timeline
    twitter_user_args.add_argument(
        '--user-id-timeline',
        type=str,
        help=aligntext('''Returns a collection of the most recent
        Tweets posted by the user indicated by the user_id.
        '''),
        metavar='id',
        dest='user_id',
        required=not '--user-name-timeline' in sys.argv
    )

    # exclude replies
    twitter_user_args.add_argument(
        '--exclude-replies',
        help=aligntext('''Prevents replies from appearing in the
        returned timeline. Default: False.
        '''),
        action='store_true',
        default=False,
        dest='exclude_replies'
    )

    # include retweets
    twitter_user_args.add_argument(
        '--include-rts',
        help=aligntext('''Includes retweets in the returned timeline.
        Default: False.
        '''),
        action='store_true',
        default=False,
        dest='include_rts'
    )

    # since id
    twitter_user_args.add_argument(
        '--since-id',
        type=str,
        help=aligntext('''Returns results with an ID greater than
        (that is, more recent than) the specified ID. Default 1.
        '''),
        metavar='id',
        default='1',
        dest='since_id'
    )

    # max id
    twitter_user_args.add_argument(
        '--max-id',
        type=str,
        help=aligntext('''Returns results with an ID less than
        (that is, older than) or equal to the specified ID.
        '''),
        metavar='id',
        dest='max_id'
    )

    # timezone
    twitter_user_args.add_argument(
        '-tz',
        '--timezone',
        type=str,
        help='Converts UTC data from posts into specified timezone',
        metavar='tz',
        dest='timezone'
    )


    '''

    Get arguments
    '''
    args = vars(parser.parse_args())
    
    '''

    Process arguments

    if not arguments:
        Trigger -> collect parameters from user
    '''
    logging.info('Collecting arguments')
    
    kwargs = ProcessArguments(args)
    args = kwargs._get_arguments()
    
    logging.info('Arguments ready')


    '''

    Connecting to service
    '''
    logging.info('Connecting to service')




    # TEST
    test_api_twitter = API(**args)

    # users
    test_data = test_api_twitter.user_timeline()


# execute
if __name__ == '__main__':
    '''

    run main function
    '''
    main()
