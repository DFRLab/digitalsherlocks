# -*- coding: utf-8 -*-

''' Export data from SQLite database.

'''

# import modules
import os
import time
import sqlite3
import argparse
import pandas as pd

# get arguments
parser = argparse.ArgumentParser()

parser.add_argument(
    '-d',
	'--database',
	required=True,
	help='Specifies SQLite database.'
)

parser.add_argument(
	'-t',
	'--table',
	type=str,
    required=True,
    choices=[
        'users', 'place', 'tweet', 'mentions', 'hashtags', 'urls',
        'media_tweet', 'media', 'media_video'
    ],
	help='SQLite database tables.'
)

parser.add_argument(
    '-o',
	'--output',
	required=True,
	help='Dataset output. This should be a directory/folder.'
)

parser.add_argument(
    '-f',
	'--format',
	required=True,
    choices=['csv', 'xlsx', 'json'],
	help='Defines data output.'
)

# parse arguments
args = vars(parser.parse_args())

# Init program
text = f'''

---
Init program at {time.ctime()}


-> Export data

'''
print (text)

# arguments
database = args['database']
output = args['output']
table = args['table']
f = args['format']

# connect to database
db_connection = sqlite3.connect(database)
cursor = db_connection.cursor()

# encoding
cursor.execute('PRAGMA encoding')

# SQLite request
sql = f"""
SELECT *
FROM {table}
"""
cursor.execute(sql)

# get data
rows = [i for i in cursor.fetchall()]
cols = [i[0] for i in cursor.description]

# build dataframe
df = pd.DataFrame(rows, columns=cols)

# save dataframe
if output.endswith('/'):
    output = output[:-1]

output = f'{output}/data/tables/'
if not os.path.exists(output):
    os.makedirs(output, exist_ok=True)

save_path = f'{output}{table}.{f}'
if f == 'json':
    df = df.to_dict(orient='records')
    obj = json.dumps(df, ensure_ascii=False, indent=2)

    # write json file
    writer = open(save_path, encoding='utf-8', mode='w')
    writer.write(obj)
    writer.close()
elif f == 'csv':
    df.to_csv(save_path, encoding='utf-8', index=False)
else:
    df.to_excel(save_path, index=False)

# close db connection
db_connection.close()

# end of programm
text = f'''
---
-> connection closed

End program at {time.ctime()}
'''
print ('')
print ('')
print (text)
