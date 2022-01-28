# -*- coding: utf-8 -*-

# =========================================
# digitalsherlocks
# A DFRLab project
#
# Author: @estebanpdl
#
# File: Telegram API client.
# =========================================

# import modules
import os
import time
import json
import requests

# import from modules
from serpapi import GoogleSearch
from urllib.parse import (
	urlparse, parse_qs
)

'''

TEMP
Arguments

'''
import argparse

# creating arguments
parser = argparse.ArgumentParser(description='Arguments.')

# require arguments
parser.add_argument(
	'--api-key',
	type=str,
	required=True,
	help='SerpAPI key.',
	metavar='KEY',
	dest='api_key'
)

# parse arguments
args = vars(parser.parse_args())

# get API Key
api_key = args['api_key']
print ('')

# search by site
sites = [
	'ria.ru',
	'russian.rt.com',
	'vesti.ru',
	'vz.ru',
	'iz.ru',
	'mk.ru',
	'lenta.ru',
	'gazeta.ru',
	'tsargrad.tv',
	'rbc.ru',
	'riafan.ru',
	'fontanka.ru'
]

queries = [
	'Наступлени AND Украин',
	'Нападени AND Украин',
	'Атак AND Украин',
	'Провокаци AND Украин',
	'Наступлени AND ВСУ',
	'Нападени AND ВСУ',
	'Атак AND ВСУ',
	'Провокаци AND ВСУ'
]

# fake output
fake_path = 'data/ukraine_crisis/requests'
fake_output = f'D:/i/repositories/DigitalResearch/{fake_path}'

# save progress
progress = open(
	f'{fake_output.replace("/requests", "")}/progress.txt',
	encoding='utf-8',
	mode='a'
)

# get progress
progress_f = f'{fake_output.replace("/requests", "")}/progress.txt'
if os.path.isfile(progress_f):
	queries_completed = [
		i.rstrip() for i in open(
			progress_f, encoding='utf-8', mode='r'
		)
	]
else:
	queries_completed = []

for s in sites:
	print (f'Collecting data from {s}')
	print ('')

	# building query
	qn = 1
	for q in queries:
		print (f'Using query: {q}')
		q = f'site:{s} {q} after:2021-11-01'

		# query audit
		q_audit = f'{q} - qn - {qn}'
		if q_audit in queries_completed:
			pass
		else:

			params = {
				'api_key': api_key,
				'engine': 'google',
				'q': q,
				'google_domain': 'google.com',
				'num': 100
			}

			# do request
			search = GoogleSearch(params)
			res = search.get_dict()

			# collect organic data
			if 'organic_results' in res.keys():
				data = res['organic_results']

				# get next < pagination >
				pag = 'serpapi_pagination'
				while True:
					if pag in res.keys():
						try:
							next_link = res[pag]['next_link']
							parsed_url = urlparse(next_link)
							start = parse_qs(
								parsed_url.query
							)['start'][0]
							start = int(start)

							# update params < search >
							params['start'] = start
							search = GoogleSearch(params)
							res = search.get_dict()

							# append data
							if 'organic_results' in res.keys():
								data.extend(
									res['organic_results']
								)
						except KeyError:
							'''
							'''
							break
					else:
						break

				# save response
				domain = s.split('.')[0]
				path = f'{fake_output}/{domain}-{qn}.json'
				obj = json.dumps(
					data, ensure_ascii=False, indent=2
				)

				# writer
				writer = open(
					path, encoding='utf-8', mode='w'
				)
				writer.write(obj)
				writer.close()

		# save progress
		progress.write(f'{q_audit}\n')
		qn += 1

# close progress
progress.close()
