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

# Welcome Message
from pyfiglet import Figlet
font = Figlet(font='big')
message = '''
    Digitalsherlocks
'''
print (font.renderText(message))




# import modules
import sys

# import from modules
from argparse import (
    ArgumentParser, RawTextHelpFormatter
)


def main():
    '''

    main function
    '''
    
    # creating parser
    parser = ArgumentParser(
        prog='digitalsherlocks'
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
        description='Allows using tool through the command line',
        help='Allows using digitalsherlocks through the command line'
    )

    '''

    CLI Arguments
    '''
    cli_args = cli.add_subparsers(
        title='CLI Arguments',
        description='',
        metavar='subcommand\n'   
    )

    '''

    Twitter CLI Arguments
    '''
    twitter = cli_args.add_parser(
        'twitter',
        description='Connects to Twitter API using user authentication',
        help='Connects to Twitter API using user authentication'
    )

    # creating Twitter argument group  
    twitter_args = twitter.add_argument_group('Arguments')

    # adding Twitter arguments
    twitter_args.add_argument(
        '--foo',
        action='store_true',
        default=False,
        help='foo'
    )

    # verify arguments
    arguments = sys.argv
    if not arguments:
        '''

        Trigger -> collect parameters from user 
        '''

        args = None

        pass

    else:
        '''

        Parse Arguments
        '''
        args = vars(parser.parse_args())

    # define arguments and type of usage
    print (args)


# execute
if __name__ == '__main__':
    '''

    run main function
    '''
    main()
