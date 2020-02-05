#! /Users/Sehokim/anaconda3/bin/python3.6
from const.basic import ROOT
from const import identity, dbconn, fbclient
from lib import fitpy
import json
import sys
import logging
import requests
import time
import random
from datetime import datetime, timedelta
import numpy as np
import pandas as pd






logging.info('> Importing token...')
with open(f'{ROOT}/var/tokens/token{identity.ID}.json', 'r') as f: 
    token = json.load(f)



# Extract


# check if the token is still valid

today = datetime.today().date()
try: fitpy.request_sleep_data(token, str(today - timedelta(days=1)), str(today))
except:
    logging.info('> Token expired, refreshing token...')
    # refresh token
    url = "https://api.fitbit.com/oauth2/token"
    headers = {
        'content-type' : 'application/x-www-form-urlencoded', 
        'authorization' : 'Basic ' + fbclient.ENCODED_CLIENT_CRED.decode('utf')
        }
    refresh_token = token['refresh_token']
    data = f'client_id={fbclient.CLIENT_ID}&grant_type=refresh_token&refresh_token={refresh_token}'
    new_token = json.loads(requests.post(url, headers=headers, data=data).text)
    # save new token to a file
    if "errors" not in new_token.keys():
        with open(f'{ROOT}/var/tokens/token{id}.json', 'w+') as f:
            json.dump(new_token, f)
    else:
        logging.critical('> failed refreshing token.')
        sys.exit()

    token = new_token




cur = dbconn.CONN.cursor()





# request current subject's sleep data since the end of the existing records
try: 
    cur.execute(f'''SELECT sj_id FROM sleep WHERE sj_id = '{identity.ID}';''')
    if cur.fetchone() == None:
        raise Exception

except: 
    dbconn.CONN.rollback()
    logging.info('> requesting sleep data...')
    sleep = fitpy.request_sleep_data(token, '2019-04-15', str(today))

else:
    cur.execute(f'''SELECT "end"::date - 1
                    FROM sleep s
                    JOIN subjects sj ON s.sj_id = sj.id
                    WHERE sj_id = '{identity.ID}'
                    ORDER BY "end"::date - 1 DESC 
                    LIMIT 1;'''
    )
    logging.info('> requesting sleep data...')
    record_end = str(cur.fetchone()[0])
    sleep = fitpy.request_sleep_data(token, record_end, str(today))







# Transform Sleep Data...
logging.info('> transforming sleep data...')
if sleep.shape[0] > 0: 
    sleep = fitpy.parse_sleep_data(sleep)
else: 
    sleep = pd.DataFrame()





# Load Data...






# Insert Sleep Data
logging.info('> inserting sleep data...')
sleep_null = sleep.fillna('null')
for ind in range(sleep.shape[0]):
    start = str(sleep_null.loc[ind, 'start'])
    end = str(sleep_null.loc[ind, 'end'])
    light = sleep_null.loc[ind, 'light']
    rem = sleep_null.loc[ind, 'rem']
    deep = sleep_null.loc[ind, 'deep']
    awakening = sleep_null.loc[ind, 'awakening']
    cur.execute(f'''INSERT INTO sleep 
                    VALUES ('{start}','{end}',{light},{rem},{deep},{awakening},'{identity.ID}')
                    ON CONFLICT (start) DO NOTHING;'''
    )
cur.close()
dbconn.CONN.commit()




# Disconnect RDS
logging.info('> disconnecting DB...')
dbconn.CONN.close()