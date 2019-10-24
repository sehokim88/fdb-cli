from const.basic import ROOT
from const import identity
import os
import logging

os.remove(f'{ROOT}/var/identity.json')
logging.info(f'{identity.NAME.capitalize()} is now logged out.')

# automatic logout after interval of time