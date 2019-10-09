from .basic import root
import json
import logging
import sys

try: 
    with open(f'{root}/var/identity.json', 'r') as f:
        identity = json.load(f)

except: 
    logging.error('ID not verified, please login first.')
    sys.exit()

else:
    type = identity['type']
    id = identity['id']
    name = identity['name']
    logging.info(f'> ID verified: {type}, {id}, {name.capitalize()}.')

logging.debug('> Importing identity constants...')



