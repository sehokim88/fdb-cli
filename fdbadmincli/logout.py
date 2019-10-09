from const.basic import root
from const import identity
import os
import logging

os.remove(f'{root}/var/identity.json')
logging.info(f'{identity.name.capitalize()} is now logged out.')

# automatic logout after interval of time