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
print ('')
print ('')

'''

Import modules
'''

import sys
import shutil

# import from modules
from argparse import (
    ArgumentParser, RawTextHelpFormatter
)

from arguments import ProcessArguments
from arguments.utils import (
    aligntext
)


def main():
    '''

    main function
    '''
    
    # creating parser
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
        help='Allows using digitalsherlocks through the command line',
        epilog='''
        
        Examples:

        $ digitalsherlocks cli twitter -h
        '''.lstrip()
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
        help='Connects to Twitter API using user authentication',
        epilog='''

        Examples:

        $ digitalsherlocks cli twitter users -h
        '''.lstrip()
    )

    # creating Twitter sub parsers
    twitter_subparsers = twitter.add_subparsers(
        title='Twitter arguments',
        description='',
        dest='group',
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
        help='Uses Twitter users-related endpoints',
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

    User timeline-related arguments
    '''

    # user name timeline
    twitter_user_args.add_argument(
        '--user-name-timeline',
        type=str,
        help=aligntext('''Returns a collection of the most recent
        Tweets posted by the user indicated by the screen_name
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
        Tweets posted by the user indicated by the user_id
        '''),
        metavar='id',
        dest='user_id',
        required=not '--user-name-timeline' in sys.argv
    )

    # exclude replies
    twitter_user_args.add_argument(
        '--exclude-replies',
        help=aligntext('''Prevents replies from appearing in the
        returned timeline. Default: False
        '''),
        action='store_true',
        default=False,
        dest='exclude_replies'
    )

    # include retweets
    twitter_user_args.add_argument(
        '--include-rts',
        help=aligntext('''Prevents retweets from appearing in the
        returned timeline. Default: False
        '''),
        action='store_true',
        default=False,
        dest='include_rts'
    )

    # get arguments
    args = vars(parser.parse_args())

    '''

    Process arguments

    if not arguments:
        Trigger -> collect parameters from user
    '''
    kwargs = ProcessArguments(args)

    # TEST get arguments
    args = kwargs._get_arguments()

    print ('')
    print ('')
    print ('')
    print (args)
    print ('')
    print ('')


# execute
if __name__ == '__main__':
    '''

    run main function
    '''
    main()
