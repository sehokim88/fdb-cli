from .basic import ROOT
import json
import logging
import sys

try: 
    with open(f'{ROOT}/var/identity.json', 'r') as f:
        identity = json.load(f)

except: 
    logging.error('ID not verified, please login first.')
    sys.exit()

else:
    TYPE = identity['type']
    ID = identity['id']
    NAME = identity['name']
    logging.info(f'> ID verified: {TYPE}, {ID}, {NAME.capitalize()}.')

logging.debug('> Importing identity constants...')



