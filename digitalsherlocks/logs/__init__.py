# -*- coding: utf-8 -*-

# =========================================
# digitalsherlocks
# A DFRLab project
#
# Author: @estebanpdl
#
# File: loggin utils.
# =========================================

# import modules
import time

# Import logs modules
from colorama import Style, Fore
from colorama import init as COLORAMA_INIT
COLORAMA_INIT()

'''

Functions

- log_time_fmt

'''

# date string
def log_time_fmt():
    '''
    
    Retrives time in the format
    %Y-%m-%d %H:%M:%S
    '''
    fmt = '%Y-%m-%d %H:%M:%S'
    return time.strftime(fmt)

# log text
def printl(text, style='BRIGHT', color='WHITE'):
    '''

    prints logs
    '''
    # Style
    s = {
        'DIM': Style.DIM,
        'NORMAL': Style.NORMAL,
        'BRIGHT': Style.BRIGHT,
        'RESET_ALL': Style.RESET_ALL
    }

    # Color
    c = {
        'BLACK': Fore.BLACK,
        'RED': Fore.RED,
        'GREEN': Fore.GREEN,
        'YELLOW': Fore.YELLOW,
        'BLUE': Fore.BLUE,
        'MAGENTA': Fore.MAGENTA,
        'CYAN': Fore.CYAN,
        'WHITE': Fore.WHITE,
        'RESET': Fore.RESET
    }

    # parameters
    st = s[style]
    fore = c[color]

    print (
        st + fore + f'{log_time_fmt()} - {text}'
    )
