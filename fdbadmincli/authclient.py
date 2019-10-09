from const.basic import root
from const import identity, fbclient
import json
import os
import logging
import flask 
import requests



app = flask.Flask(__name__, static_url_path='')



@app.route('/')
def home():
    # get code
    try:
        code = flask.request.query_string.decode('utf-8')[5:]
        
        # request token
        url = "https://api.fitbit.com/oauth2/token"
        headers = {
            'content-type' : 'application/x-www-form-urlencoded', 
            'authorization' : 'Basic ' + fbclient.encoded_client_cred.decode('utf')
            }
        data = f'client_id={fbclient.client_id}&grant_type=authorization_code&redirect_uri=http%3A%2F%2F127.0.0.1%3A5000&code={code}'
        token = json.loads(requests.post(url, headers=headers, data=data).text)

        # export token
        if 'tokens' not in os.listdir('var'): os.mkdir('var/tokens/')
        with open(f'{root}var/tokens/token{identity.id}.json', '+w') as f:
            json.dump(token, f)
        return 'token dumped'
        
    except:
        return 'heller'        




