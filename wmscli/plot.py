from config import *
from check_identity import user_id
from db_conn import conn
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
from datetime import datetime
import scipy.stats as ss
register_matplotlib_converters()



cur = conn.cursor()


query = f"""
SELECT start::time start_time,
    CASE WHEN EXTRACT( EPOCH FROM start::time ) < 60*60*12 THEN EXTRACT( EPOCH FROM start::time ) + 60*60*24
        ELSE EXTRACT( EPOCH FROM start::time )
        END::real/60 start_epoch,
    EXTRACT( week FROM "end"::date -1 )::int2 "week",
    "end"::date-1 "date"
FROM sleep
JOIN users USING ("userID")
WHERE NOW()-("end"::date-1) < INTERVAL '6 months' 
AND "userID" = '{user_id}'
AND "end"-start > INTERVAL '3.5 hours'
ORDER BY start;
"""

# query and fetch the database
logging.info('> querying data...')
cur.execute(query)
data = cur.fetchall()
colnames = [cn[0] for cn in cur.description]
sleep_start_time_with_week = pd.DataFrame(data, columns=colnames)


# calculate weekly aggregated statistics
logging.info('> formulating statistics...')
weekly_avg_df = sleep_start_time_with_week.groupby('week').mean().reset_index()
weekly_std_df = sleep_start_time_with_week.groupby('week').std().reset_index()
weekly_stats_df = weekly_avg_df.merge(weekly_std_df, on='week')
weekly_stats_df.columns = ['week', 'avg', 'std']

get_time = lambda x: datetime.strftime(x,'%H:%M:%S')
weekly_stats_df['time'] = pd.to_datetime(weekly_stats_df['avg']*60, unit='s').apply(get_time)

last_ind = weekly_stats_df.shape[0]-2
overall_avg_std = weekly_stats_df.loc[:last_ind ,'std'].mean()
get_pct_change_from_overall = lambda x: (x - overall_avg_std) / overall_avg_std
weekly_stats_df['comp'] = weekly_stats_df['std'].apply(get_pct_change_from_overall)   



# generate and save a boxplot
logging.info('> generating inconsistency boxplot...')
fig = plt.figure(figsize=(10,3))
grid = plt.GridSpec(1,1)
ax1 = plt.subplot(grid[0,0])

ax1.boxplot(
    weekly_stats_df.loc[weekly_stats_df.notna().all(1),'std'],
    labels=[''],
    widths=[0.25],
    vert=False,
    medianprops={'color':'black'}
)
ax1.set_title('Inconsistency Measure for Sleep Start Time')
ax1.set_xlabel('Inconsistency Measure (STD by Weeks in Minutes)')

for i, j in enumerate(list(range(-4,0))):
    size = np.exp(i+2)+10
    consistency_score = weekly_stats_df['std'].values[j]
    week = weekly_stats_df['week'].values[j]
    label= f"{week}th Week"
    if j == -1:
        color='red'
    else: color='black'
    ax1.scatter(consistency_score, 1, c=color, s=size, label=label, marker=',')
        
ax1.legend()





new_file_name = 'inconsistency.png'

logging.info(f'> saving as "img/{new_file_name}"...')
fig.savefig(f'{root}/img/{new_file_name}', bbox_inches='tight')




































query = f"""
SELECT start::time start_time,
    CASE WHEN EXTRACT( EPOCH FROM start::time ) > 60*60*12 THEN EXTRACT( EPOCH FROM start::time )
        ELSE EXTRACT( EPOCH FROM start::time ) + 60*60*24
        END::real / 60 start_epoch,
    EXTRACT( DOW FROM "end"::date -1 )::int2 dow,
    "end"::date-1 "date"
FROM sleep
JOIN users USING ("userID")
WHERE "userID" = '{user_id}'
AND EXTRACT( EPOCH FROM "end"-start )::dec/60/60 >= 3
AND NOW() - ("end"::date-1) < INTERVAL '6 month'
ORDER BY start ASC;
"""

# query and fetch the database
logging.info('> querying data...')
cur.execute(query)
data = cur.fetchall()
colname = [c[0] for c in cur.description]
sleep_start_with_dow = pd.DataFrame(data, columns=colname)









# calculate weekly aggregated statistics
logging.info('> formulating statistics...')
sun = sleep_start_with_dow.loc[sleep_start_with_dow['dow'] == 0]
mon = sleep_start_with_dow.loc[sleep_start_with_dow['dow'] == 1]
tue = sleep_start_with_dow.loc[sleep_start_with_dow['dow'] == 2]
wed = sleep_start_with_dow.loc[sleep_start_with_dow['dow'] == 3]
thu = sleep_start_with_dow.loc[sleep_start_with_dow['dow'] == 4]
fri = sleep_start_with_dow.loc[sleep_start_with_dow['dow'] == 5]
sat = sleep_start_with_dow.loc[sleep_start_with_dow['dow'] == 6]
most_recent_by_dow = []
dow_digits = []
for dow_digit, dow in enumerate([sun,mon,tue,wed,thu,fri,sat]):
    most_recent_by_dow.append(dow.reset_index().loc[dow.shape[0]-1, 'start_epoch'])
    dow_digits.append(dow_digit+1)
week_avg_start_time = np.mean(most_recent_by_dow)










# generate and save a boxplot
logging.info('> generating sleep-time boxplot...')
fig = plt.figure(figsize=(10,6))
fig.subplots_adjust(hspace=0.4, wspace=0.4)
grid = plt.GridSpec(4,1)


ax1 = plt.subplot(grid[1:,0])
ax1.boxplot(
    [sun['start_epoch'].values,
     mon['start_epoch'].values,
     tue['start_epoch'].values,
     wed['start_epoch'].values,
     thu['start_epoch'].values,
     fri['start_epoch'].values,
     sat['start_epoch'].values],
    labels=['S', 'M', 'T', 'W', 'Th', 'F', 'Sa'],
    widths=0.5,
    vert=False,
    showfliers=False,
    medianprops={'color':'black'}
)

ax1.set_xticks(np.linspace(0,30*60,31))
ax1.set_xticklabels([datetime.utcfromtimestamp(t*60).strftime('%H:%M') for t in np.linspace(0,30*60,31)])
ax1.set_xlim(18*60, 31*60)
ax1.set_xlabel('Average Sleep Start Time')
ax1.set_ylabel('Day of the Week')

ax1.scatter(most_recent_by_dow, dow_digits, c='red', s=20, label='Most Recent Recordings', marker=',')
ax1.axvline(week_avg_start_time, linestyle='--', c='red', linewidth=0.5, label='AVG of the 7 Most Recent Recordings')
ax1.legend()


ax2 = plt.subplot(grid[0,0], sharex=ax1)
ax2.boxplot(
    sleep_start_with_dow['start_epoch'],
    labels=['All'],
    widths=0.3,
    vert=False,
    showfliers=False,
    medianprops={'color':'black'}
)
ax2.set_title('Sleep Start Time Distribution by DOW for the past 6 months')



# save figure
new_file_name = 'sleep-time.png'
logging.info(f'> saving as "img/{new_file_name}"...')
fig.savefig(f'{root}/img/{new_file_name}', bbox_inches='tight')





# close DB connection
logging.info('> closing DB connection...')
cur.close()
conn.close()