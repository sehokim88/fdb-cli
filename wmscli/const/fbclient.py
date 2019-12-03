from .basic import ROOT
import yaml
import logging
from base64 import b64encode
 


with open(f'{ROOT}/var/config.yaml', 'r') as f:
    config_yaml = yaml.load(f, Loader=yaml.SafeLoader)

app_creds = config_yaml['app']

CLIENT_ID = client_id = app_creds['client_id']
CLIENT_SECRET = app_creds['client_secret']
ENCODED_CLIENT_CRED = b64encode(bytes(f'{CLIENT_ID}:{CLIENT_SECRET}', 'utf'))

logging.debug('> Importing fbclient constants...')