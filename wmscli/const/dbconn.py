from .basic import ROOT
import yaml
import logging
import psycopg2 as pg


with open(f'{ROOT}/var/config.yaml', 'r') as f:
    config_yaml = yaml.load(f, Loader=yaml.SafeLoader)
    
db = config_yaml['db']

logging.debug('> Connecting to DB...')
CONN = pg.connect(
    host=db['host'], 
    port=db['port'], 
    user=db['user_id'], 
    database=db['database'], 
    password=db['password']
)

logging.debug('> Importing DB connection...')

