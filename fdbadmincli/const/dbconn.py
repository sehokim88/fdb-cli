from .basic import root
import yaml
import logging
import psycopg2 as pg


with open(f'{root}/var/config.yaml', 'r') as f:
    config_yaml = yaml.load(f)
    
db = config_yaml['db']
db_host = db['host']
db_port = db['port']
db_name = db['database']
db_user_id = db['user_id']
db_pwd = db['password']


logging.debug('> Connecting to DB...')
conn = pg.connect(host=db_host, port=db_port, user=db_user_id, database=db_name, password=db_pwd)

logging.debug('> Importing DB connection...')

