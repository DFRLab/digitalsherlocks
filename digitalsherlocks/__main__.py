# -*- coding: utf-8 -*-

# =========================================
# digitalsherlocks
# A DFRLab project - @estebanpdl
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






from APITwitter.client import TwitterAuthentication


TwitterAuth = TwitterAuthentication()
TwitterAPI = TwitterAuth.connect()

