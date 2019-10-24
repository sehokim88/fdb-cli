from const.basic import ROOT
from const import identity, fbclient
import json
import os
import logging
import flask 
import requests



app = flask.Flask(__name__, static_url_path='')



@app.route('/')
def home():
    
    try:
        logging.debug('> Retrieving the code...') # get code
        code = flask.request.query_string.decode('utf-8')[5:]
        
        logging.debug('> Requesting the token...') # request token
        url = "https://api.fitbit.com/oauth2/token"
        headers = {
            'content-type' : 'application/x-www-form-urlencoded', 
            'authorization' : 'Basic ' + fbclient.ENCODED_CLIENT_CRED.decode('utf')
            }
        data = f'client_id={fbclient.CLIENT_ID}&grant_type=authorization_code&redirect_uri=http%3A%2F%2F127.0.0.1%3A5000&code={code}'
        token = json.loads(requests.post(url, headers=headers, data=data).text)

        logging.debug('> Dumping the token...') # dump token
        if 'tokens' not in os.listdir('var'): os.mkdir('var/tokens/')
        with open(f'{ROOT}/var/tokens/token{identity.ID}.json', '+w') as f:
            json.dump(token, f) 
        return 'token dumped'
        
    except:
        return 'heller'    


if __name__ == '__main__':
    app.run(host='127.0.0.1', port='5000')    




