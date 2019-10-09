from .config import *
from base64 import b64encode
 


with open(f'{root}/var/config.yaml', 'r') as f:
    config_yaml = yaml.load(f)

app_creds = config_yaml['app']

client_id = app_creds['client_id']
client_secret = app_creds['client_secret']
encoded_client_cred = b64encode(bytes(f'{client_id}:{client_secret}', 'utf'))