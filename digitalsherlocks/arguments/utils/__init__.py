# -*- coding: utf-8 -*-

# =========================================
# digitalsherlocks
# A DFRLab project
#
# Author: @estebanpdl
#
# File: Arguments utils.
# =========================================

'''

Functions:

	- aligntext
'''

def aligntext(text):
	'''

	Removes newlines and extra spaces in text
	'''
	return ' '.join(text.split()).strip()
