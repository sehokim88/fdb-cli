from .config import *



try: 
    with open(f'{root}/var/identity.json', 'r') as f:
        identity = json.load(f)

    account_type = identity['account_type_abb']
    user_id = identity['user_id']
    user_name = identity['user_name']

    logging.info(f'User Name: {user_name.capitalize()}')

except: 
    logging.info('Please login first.')
    sys.exit()

