# -*- coding: utf-8 -*-

''' Twitter API file.

'''

# Introduce Message
from pyfiglet import Figlet
font = Figlet(font='big')
message = '''   DFRLAB
    Digital
    Sherlocks
'''
print (font.renderText(message))

# import modules
import sqlite3
import time

# import local modules
from utils import nl, collect_parameters, create_db_file

# import api module
from api import api

# Init program
text = f'''

Init program at {time.ctime()}

'''
print (text)

# collect attrs from user
parameters = collect_parameters()
nl()
print ('> Parameters ready to use.')
print (parameters)
try:
    update_status = False if parameters[1]['since_id'] == '1' else True
except KeyError:
    update_status = False
nl()

# create or add a .db file
if update_status:
    database = input('Add path to an existing database: ')
    db_connection = sqlite3.connect(database)

    # get cursor
    cursor = db_connection.cursor()
else:
    nl()
    print ('Creating a database.')
    workspace = input('Add working directory: ')
    sqlfile = input('Add sql file: ')
    nl()
    db_connection, cursor = create_db_file(
        workspace,
        sqlfile
    )
    print ('> done.')
    nl()

# add db connection and cursor to parameters
db_attrs = (db_connection, cursor,)
parameters = db_attrs + parameters

# send parameters to API.
nl()
if parameters[2] in ['keyword', 'profile']:
    key = 'q' if parameters[2] == 'keyword' else 'screen_name'
    query = parameters[3][key]
    print ('Downloading tweets')
    print ('Depending on the number of tweets, task could take several minutes.')
    print (f'Query: {query}')
    print ('...')
    api_connection = api(*parameters)
    print ('> done.')
    nl()
else:
    print ('Downloading user connections')
    print ('Time will depend on the number of connections.')
    print ('...')
    api_connection = api(*parameters)


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
