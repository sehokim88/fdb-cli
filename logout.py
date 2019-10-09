from lib.config import *
from lib.identity import user_name

os.remove(f'{root}/var/identity.json')
logging.info(f'{user_name.capitalize()} is now logged out.')

