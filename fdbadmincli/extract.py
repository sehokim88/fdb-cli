from const.basic import ROOT
from const import identity, dbconn
import logging
import pandas as pd

# check the user's account-type
if identity.TYPE == 'subscriber':
    pass
else:
    logging.error('Only subscriber can extract data.')
    
# check subjects belong to the subscriber
cur = dbconn.CONN.cursor()
cur.execute(f'''SELECT sj.id 
            FROM subjects sj 
            JOIN subscribers ss ON sj.ss_id = ss.id
            WHERE ss.id = '{identity.ID}';''')
subject_ids = [row[0] for row in cur.fetchall()]
subject_ids_str = ''
for i, x in enumerate(subject_ids):
    if i == 0:
        subject_ids_str += str(x)
    else:
        subject_ids_str += f', {str(x)}'
logging.info(f'''> Subscriber {identity.ID}'s subjects: {subject_ids_str}''')

# export sleep df into csv file
for sj_id in subject_ids:
    logging.info(f'''> exporting subject{sj_id}'s sleep data...''')
    cur.execute(f'''SELECT * FROM sleep s WHERE sj_id = {sj_id};''')
    data = cur.fetchall()
    colnames = [cn[0] for cn in cur.description]
    df = pd.DataFrame(data, columns=colnames)
    df.to_csv(f'{ROOT}/data/sleep-sj{sj_id}-ss{identity.ID}.csv')