import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import requests
import json
import logging





def datespace(start, end, step=1):
    """
    INPUT:
        start: date string in '%Y-%m-%d'
        end: date string in '%Y-%m-%d'

    OUTPUT:
        list of datetime.date objects ranging from the given start and end date
    """
    if start <= end:
        a = datetime.strptime(start, '%Y-%m-%d')
        z = datetime.strptime(end, '%Y-%m-%d')
        result = []
        result.append(a.date())
        while z > a:
            a += timedelta(days=step)
            if a <= z:
                result.append(a.date())
        return result
    else: 
        raise ValueError('Start Date cannot be before End Date.')







def get_delta(df):
    """
    takes in two datetime columns
    returns datetime column with timedelta between the two points in time.
    """
    df = df.copy()
    bracket = np.zeros(df.shape[0])
    bracket[1:] = df.loc[1:,'start'].values - df.loc[:df.shape[0]-2, 'end'].values
    return bracket/60000000000 







def request_sleep_data(token: dict, start_date: str, end_date: str) -> pd.DataFrame:
    """
    "Request call to Fitbit API for Time-Series Sleep data, following OAuth 2.0 Authorization Code Flow Protocol. "

    INPUT:
        token: Token data in JSON format, a response from the token request with URL encoded code after
                user login. 
        start_date: date string of which the query begins. 
        end_date: date string of which the query ends. 
    OUTPUT:
        new_df: a DataFrame of concatenated time-series sleep data within the date range specified.  
    """
    uuid = token['user_id']
    access_token = token['access_token']
    token_type = token['token_type']

    headers = {
        'content-type' : 'application/json', 
        'authorization' : token_type + " " + access_token
        }
    
    s = datetime.strptime(start_date, '%Y-%m-%d')
    e = datetime.strptime(end_date, '%Y-%m-%d')

    if (e-s).days >= 100:
        new_df = pd.DataFrame()
        date_interval = datespace(start_date, end_date, step=100)
        for i_date in date_interval:
            j_date = i_date + timedelta(days=99)
            endpoint = f'https://api.fitbit.com/1.2/user/{uuid}/sleep/date/{i_date}/{j_date}.json'
            res = requests.get(endpoint, headers = headers)
            new_data = json.loads(res.text)
            if 'sleep' in new_data.keys(): 
                new_df = pd.concat([new_df, pd.DataFrame(new_data['sleep'])])
            else: 
                logging.error(f'''{new_data['errors'][0]['message']}''')
                raise Exception

        new_df.sort_values('startTime', inplace=True)
        new_df.reset_index(inplace=True, drop=True)

    else: 
        endpoint = f'https://api.fitbit.com/1.2/user/{uuid}/sleep/date/{start_date}/{end_date}.json'
        res = requests.get(endpoint, headers = headers)
        new_data = json.loads(res.text)
        
        if 'sleep' in new_data.keys(): 
            new_df = pd.DataFrame(new_data['sleep'])
        else: 
            logging.error(f'''{new_data['errors'][0]['message']}''')
            raise Exception
      
    return new_df







def parse_datetime(time_str, out_format='datetime'):
    """Reads time_str in any format and writes a datetime, date, or time obejct.
    
    INPUT:
        time_str: time string in any format
        out_format: datetime, date, or time
    
    OUTPUT:
        parsed time_string
    """
    in_formats = ['%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%d %H:%M:%S.%f', 
                  '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', 
                  '%Y-%m-%dT%I:%M%p', '%Y-%m-%d %I:%M%p',
                  '%Y-%m-%d']
    for f in in_formats:
        try:
            if out_format == 'datetime':
                return datetime.strptime(time_str, f)
            elif out_format == 'date':
                return datetime.strptime(time_str, f).date()
            elif out_format == 'time':
                return datetime.strptime(time_str, f).time()
        except:
            raise ValueError






def parse_stage(x, stage='deep'):
    """Parse a Fitbit-generated nested dictionary of sleep stage data 
    and returns a specified stage data.
    
    INPUT:
        x: a nested dictionary
        stage: sleep stage

    OUTPUT:
        minutes or counts of each specified sleep stage
    """
    try:
        if stage in ['deep','rem','light']:
            return x['summary'][stage]['minutes']
        elif stage == 'wake':
            return x['summary'][stage]['count']
    except:
        return np.nan 





def parse_sleep_data(sleep_df: pd.DataFrame) -> pd.DataFrame:
    """
    "Parses a raw sleep dataframe formulated with Fitbit's nested json data."

    INPUT:
        df: dataframe outputted from request_sleep_data()
    OUTPUT:
        new_df: parsed and reformated dataframe with new column names. 
        Columns include 'start', 'end', 'light', 'deep', 'rem', 'awakening'.
    """
    new_df = pd.DataFrame()
    new_df['start'] = sleep_df['startTime'].apply(parse_datetime)
    new_df['end'] = sleep_df['endTime'].apply(parse_datetime)     
    new_df['light'] = sleep_df['levels'].apply(parse_stage, stage='light')
    new_df['rem'] = sleep_df['levels'].apply(parse_stage, stage='rem')
    new_df['deep'] = sleep_df['levels'].apply(parse_stage, stage='deep')
    new_df['awakening'] = sleep_df['levels'].apply(parse_stage, stage='wake')

    new_df.sort_values('start', inplace=True)
    new_df.reset_index(inplace=True, drop=True)
    return new_df









def stitch_sleep(df):
    """
    takes in a Fitbit style dataframe and return a new DataFrame 
    with sleep logs that are less than 120 minutes apart from one another stitched together into a one sleep log. 
    
    INPUT: 
        df: dataframe with sparse 
    """
    new_df=df.copy()
    later = np.where((get_delta(new_df) < 120) & (get_delta(new_df) > 0))[0]
    earlier = later - 1
    stitch_ind = list(zip(earlier, later))
    for e, l in stitch_ind:
        new_start = new_df.loc[e,'start']
        new_end = new_df.loc[l,'end']
        new_bed = (new_df.loc[l,'end'] - new_df.loc[e,'start']).seconds/60
        new_asleep = new_df.loc[l, 'asleep'] + new_df.loc[e, 'asleep']
        new_effi = int(round(new_asleep / new_bed * 100, 0))
        if pd.notna(new_df.loc[l,'deep'] + new_df.loc[e, 'deep']):
            new_deep = new_df.loc[l,'deep'] + new_df.loc[e, 'deep']
        else: new_deep = np.nan

        if pd.notna(new_df.loc[l,'rem'] + new_df.loc[e, 'rem']):
            new_rem = new_df.loc[l,'rem'] + new_df.loc[e, 'rem']
        else: new_rem = np.nan

        if pd.notna(new_df.loc[l,'awake'] + new_df.loc[e, 'awake']):
            new_awake = new_df.loc[l,'awake'] + new_df.loc[e, 'awake'] + (new_df.loc[l, 'start']-new_df.loc[e,'end']).seconds/60%1440
        else: new_awake = np.nan

        if pd.notna(new_df.loc[l,'awakening'] + new_df.loc[e, 'awakening']):
            new_awakening = new_df.loc[l,'awakening'] + new_df.loc[e, 'awakening']
        else: new_awakening = np.nan
        
        new_dict = {'start':new_start, 'end':new_end, 'bed':new_bed, 'asleep':new_asleep, 'deep':new_deep, 'rem':new_rem, 'effi':new_effi, 'awakening':new_awakening, 'awake': new_awake}

        new_df.drop([e,l], inplace=True)        
        new_df = pd.concat([new_df, pd.DataFrame(new_dict, index=[100])], sort=False)
    new_df.sort_values('start', inplace=True)
    new_df.reset_index(inplace=True, drop=True)
    return new_df





def filter_night_main_sleep(df):
    """
    returns dataframe consisting of only night_main_sleep 
    """
    night_main_sleep_mask = \
    ((df['start'].apply(lambda x: x.time()) >= datetime(1,1,1,17,0).time()) |\
    (df['start'].apply(lambda x: x.time()) < datetime(1,1,1,5,0).time())) &\
    (df['asleep'] >= 180)

    new_df = df.loc[night_main_sleep_mask, :].copy()
    new_df.reset_index(inplace=True, drop=True)
    return new_df





def filter_day_short_sleep(df):
    """
    returns dataframe consisting of only day_short_sleep 
    """
    day_short_sleep_mask = \
    (df['start'].apply(lambda x: x.time()) > datetime(1,1,1,10,0).time()) &\
    (df['start'].apply(lambda x: x.time()) < datetime(1,1,1,22,0).time()) &\
    (df['asleep'] < 180)

    new_df = df.loc[day_short_sleep_mask, :].copy()
    new_df.reset_index(inplace=True, drop=True)
    return new_df
   




def filter_day_main_sleep(df):
    """
    returns dataframe consisting of only day_main_sleep
    """
    day_main_sleep_mask = \
    (df['start'].apply(lambda x: x.time()) > datetime(1,1,1,5,0).time()) &\
    (df['start'].apply(lambda x: x.time()) < datetime(1,1,1,17,0).time()) &\
    (df['asleep'] >= 180)

    new_df = df.loc[day_main_sleep_mask, :].copy()
    new_df.reset_index(inplace=True, drop=True)
    return new_df





def filter_night_short_sleep(df):
    """
    returns dataframe consisting of only night_short_sleep
    """
    night_short_sleep_mask = \
    ((df['start'].apply(lambda x: x.time()) >= datetime(1,1,1,22,0).time()) |\
    (df['start'].apply(lambda x: x.time()) < datetime(1,1,1,10,0).time())) &\
    (df['asleep'] < 180)
    
    new_df = df.loc[night_short_sleep_mask, :].copy()
    new_df.reset_index(inplace=True, drop=True)
    return new_df

