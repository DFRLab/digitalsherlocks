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

'''

Functions

- log_time_fmt

'''

def log_time_fmt():
    '''
    
    Retrives time in the format
    %Y-%m-%d %H:%M:%S
    '''
    fmt = '%Y-%m-%d %H:%M:%S'
    return time.strftime(fmt)
