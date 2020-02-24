#! /Users/Sehokim/anaconda3/bin/python3.6
from const.basic import ROOT
from const import dbconn, fbclient
from lib import fitpy
import json
import os
import sys
import logging
import requests
import time
import random
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from contextlib import closing


logging.basicConfig(level=logging.INFO)


with closing(dbconn.CONN.cursor()) as cur:

    cur.execute(f'''SELECT s.id sj_id, t.access_token access_token, t.refresh_token refresh_token, t.fitbit_id fitbit_id 
                    FROM tokens t 
                    JOIN subjects s 
                    ON t.id = s.token_id;''')
    tokens = cur.fetchall()
    fields = [f[0] for f in cur.description]
    if tokens:
        pass
    else:
        raise Exception

    
for token in tokens:
    token = {k:v for k, v in zip(fields, token)}
    sj_id = token['sj_id']
    fitbit_id = token['fitbit_id']




    # check if the token is still valid
    try:
        today = datetime.today().date()
        try: fitpy.request_sleep_data(token, str(today - timedelta(days=1)), str(today))
        except:
            logging.debug('> token expired, refreshing token...') # refresh token
            
            url = "https://api.fitbit.com/oauth2/token"
            headers = {
                'content-type' : 'application/x-www-form-urlencoded', 
                'authorization' : 'Basic ' + fbclient.ENCODED_CLIENT_CRED.decode('utf')
                }
            refresh_token = token['refresh_token']
            data = f'client_id={fbclient.CLIENT_ID}&grant_type=refresh_token&refresh_token={refresh_token}'
            new_token = json.loads(requests.post(url, headers=headers, data=data).text)

            
            if "errors" not in new_token.keys():
                with closing(dbconn.CONN.cursor()) as cur:
                    logging.debug('> Updating new token in tokens table...')
                    cur.execute(f'''UPDATE tokens 
                                    SET access_token = '{new_token['access_token']}',
                                        refresh_token = '{new_token['refresh_token']}'
                                    WHERE fitbit_id = '{fitbit_id}' RETURNING id
                                    ''')
                    result = cur.fetchone()
                    if result:
                        dbconn.CONN.commit()
                        pass
                    else:
                        raise Exception
                
                # logging.debug('> Dumping a new token...') # dump new token
                # with open(f'{ROOT}/var/tokens/token{sj_id}.json', 'w+') as f:
                #     json.dump(new_token, f)
            else:
                logging.error(f'''{new_token['errors'][0]['message']}''') # failed refreshing token
                sys.exit()

            token = new_token

    except:
        continue
    
    else:
        with closing(dbconn.CONN.cursor()) as cur:
            # extract sleep data
            # request current subject's sleep data since the end of the existing records
            logging.debug('> Extracting sleep data...') 
            try: 
                cur.execute(f'''SELECT sj_id FROM sleep WHERE sj_id = '{sj_id}';''')
                if cur.fetchone() == None:
                    raise Exception

            except: 
                dbconn.CONN.rollback()
                sleep = fitpy.request_sleep_data(token, '2019-04-15', str(today))

            else:
                cur.execute(f'''SELECT "end"::date - 1
                                FROM sleep s
                                JOIN subjects sj ON s.sj_id = sj.id
                                WHERE sj_id = '{sj_id}'
                                ORDER BY "end"::date - 1 DESC 
                                LIMIT 1;'''
                )
                record_end = str(cur.fetchone()[0])
                sleep = fitpy.request_sleep_data(token, record_end, str(today))









        # Transform Sleep Data...
        logging.debug('> Transforming sleep data...') 
        if sleep.shape[0] > 0: 
            sleep = fitpy.parse_sleep_data(sleep)
        else: 
            logging.debug('> No new data...') # No new data
            sleep = pd.DataFrame()











        with closing(dbconn.CONN.cursor()) as cur:
            # Load Sleep Data
            logging.debug('> Loading sleep data...') 
            sleep_null = sleep.fillna('null')
            for ind in range(sleep.shape[0]):
                start = str(sleep_null.loc[ind, 'start'])
                end = str(sleep_null.loc[ind, 'end'])
                light = sleep_null.loc[ind, 'light']
                rem = sleep_null.loc[ind, 'rem']
                deep = sleep_null.loc[ind, 'deep']
                awakening = sleep_null.loc[ind, 'awakening']
                cur.execute(f'''INSERT INTO sleep 
                                VALUES ('{start}','{end}',{light},{rem},{deep},{awakening},{sj_id})
                                ON CONFLICT (start) DO NOTHING;'''
                )
        
        dbconn.CONN.commit()
        logging.info(f'''ETL Completed for {sj_id} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}''')




# Disconnect RDS
logging.debug('> disconnecting DB...')
dbconn.CONN.close()

