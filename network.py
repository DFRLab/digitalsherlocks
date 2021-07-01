# -*- coding: utf-8 -*-

''' Creates a network-like dataset.

'''

# import modules
from tqdm import tqdm
import networkx as nx
import pandas as pd
import argparse
import sqlite3
import time
import os

# import local modules
from utils import nl, write_record, evalmentions


# get arguments
parser = argparse.ArgumentParser()

parser.add_argument(
    '-d',
	'--database',
	required=True,
	help='Specifies SQLite database.'
)
parser.add_argument(
    '-o',
	'--output',
	required=True,
	help='Dataset output. This should be a directory/folder.'
)
parser.add_argument(
    '-s',
    '--since-id',
    required=False,
    help='Since id value'
)

# parse arguments
args = vars(parser.parse_args())

# Init program
text = f'''

---
Init program at {time.ctime()}


-> Creating a network-like dataset

'''
print (text)

# arguments
database = args['database']
output = args['output']

# connect to database
db_connection = sqlite3.connect(database)
cursor = db_connection.cursor()

# encoding
cursor.execute('PRAGMA encoding')

# SQLite request
sql = """
SELECT *
FROM tweet
"""
cursor.execute(sql)

# get data
rows = [i for i in cursor.fetchall()]
cols = [i[0] for i in cursor.description]

# building dataframe
nl()
print ('--> Building dataframe')
df = pd.DataFrame(rows, columns=cols)

'''

filter dataframe if since_id parameter is included
'''
if args['since_id'] != None:
    df = df[df['id'] >= args['since_id']].copy()

# add tweet url
df['tweet_url'] = 'https://twitter.com/i/web/status/' + df['id_str']

# fix text if text starts with an URL
df['text'] = [
    (f'_{i}' if i.startswith('http') else i) for i in df['text']
]

df['full_text'] = [
    (f'_{i}' if i.startswith('http') else i) for i in df['full_text']
]

# dataframe done
print ('--> done.')
nl()
nl()

# saving dataframe
nl()
print ('--> Saving dataframe')
if output.endswith('/'):
    output = output[:-1]

output = f'{output}/data/network/'
if not os.path.exists(output):
    os.makedirs(output, exist_ok=True)

path = f'{output}network_data.csv'
df.to_csv(
    path,
    index=False,
    encoding='utf-8'
)

print ('--> done.')
nl()

# store edges in csvfile -> create empty csv file
cols = [
    'source', 'target', 'connection_type', 'software', 'sequence', 'date',
    'timestamp', 'tweet_id'
]
empty = pd.DataFrame(columns=cols)
edges_path = f'{output}edges.csv'
empty.to_csv(
    edges_path, encoding='utf-8', index=False, mode='w'
)

# iterate over each record in dataset
nl()
print ('--> Working on data records')
nl()
nl()

# dimensions and progress bar
shape = df.shape
n_records = shape[0]
pbar = tqdm(total=n_records)
for row in range(n_records):
    '''
    expected output

    - Source: main username
    - Target: connected user (retweet, reply, mention)

    '''

    # get record
    record = dict(df.iloc[row])

    # get attrs
    source = record['screen_name']

    # eval retweets
    tweet_type = record['is_retweet_status']
    if tweet_type == 1:
        target = record['rt_user_screen_name']
        cnx_type = 'retweet'

        # write record
        write_record(record, target, cnx_type, row, edges_path)
    else:
        quote = record['is_quote_status']
        if quote == 1:
            target = record['quoted_user_screen_name']
            cnx_type = 'quote'

            # write record
            write_record(record, target, cnx_type, row, edges_path)

            # find reply and mentions
            evalmentions(record, row, edges_path)
        else:
            # find reply and mentions in single post (Not a retweet, Not a quote)
            evalmentions(record, row, edges_path)
    
    # update pbar
    pbar.update(1)

# close pbar connection
pbar.close()

# close sqlite connection
db_connection.close()

'''

Create Network
'''
nl()
nl()
nl()
print ('--> Building network')

# read network
converters = {
    'date': str
}

network = pd.read_csv(
    edges_path,
    encoding='utf-8',
    converters=converters
)

# network graph
G = nx.from_pandas_edgelist(
    network,
    edge_attr=True,
    create_using=nx.MultiGraph()
)

size = G.size()
print (f'--> Network size: {size}')

# get nodes
nodes = list(G.nodes)
print (f'--> Nodes in network: {len(nodes)}')

# build nodes dataframe
df_nodes = pd.DataFrame(
    {
        'id': nodes,
        'label': nodes
    }
)

# add activity
df['label'] = df['screen_name'].str.lower()
gpo = df.groupby('label').agg(
    {
        'counter': sum
    }
).reset_index()

# filter group
filter_gpo = gpo[gpo['label'].isin(nodes)].copy()

# merge df nodes
df_nodes = df_nodes.merge(filter_gpo, how='left', on='label')
df_nodes['counter'] = df_nodes['counter'].fillna(0).astype(int)

# rename counter column to activity
df_nodes.rename(columns={'counter': 'activity'}, inplace=True)

# add degree metrics -> creating temp DiGraph
di_graph = nx.from_pandas_edgelist(
    network,
    edge_attr=True,
    create_using=nx.DiGraph()
)

degree_metrics = {
    'degree': list(dict(di_graph.degree).items()),
    'in-degree': list(dict(di_graph.in_degree).items()),
    'out-degree': list(dict(di_graph.out_degree).items())
}

# merge new attrs to df nodes
for k in degree_metrics.keys():
    d = degree_metrics[k]
    f = pd.DataFrame(d, columns=['label', k])

    # merge
    df_nodes = df_nodes.merge(f, how='left', on='label')

# save nodes
nodes_path = f'{output}nodes.csv'
df_nodes.to_csv(
    nodes_path,
    index=False,
    encoding='utf-8'
)

# end program
end = time.ctime()
nl()
nl()
nl()
print (f'End program --> {end}')
nl()
