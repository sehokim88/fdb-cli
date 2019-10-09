from lib.config import root
from lib.db_conn import conn
from getpass import getpass
from datetime import datetime
import string


# python sign-up.py {subscriber} {email} {pwd} {first_name} {last_name} {dob} {role}
# python sign-up.py {subject} {email} {pwd} {first_name} {last_name} {dob} {uuid} {ss_id}
# verify pwd security on client side first then pass to the server 




def restricted_getpass(prompt):
    retype_attempts = 0
    while retype_attempts < 5:
        values = []
        for i in range(2):
            attempts = 0
            while attempts < 5:
                if i == 1: 
                    value = getpass(f'{prompt} (retype)')
                else:
                    value = getpass(f'{prompt}')
                cond1 = len(value) > 6
                cond2 = sum([l in string.ascii_letters for l in value]) > 0
                cond3 = sum([d in string.digits for d in value]) > 0
                attempts += 1
                if cond1 and cond2 and cond3:
                    values.append(value)
                    break
                else: 
                    logging.warning('Password must contain at least one letter and one digit and longer than 6 letter-digit combinations.')
            if attempts == 5: sys.exit()
        retype_attempts += 1
        if values[0] == values[1]: 
            return values[0]
        else: 
            logging.warning('Two passwords do not match, try again.')
    sys.exit()


        



def restricted_input(prompt, is_date=False, is_email=False):
    attempts = 0
    while attempts < 5:
        value = input(f'{prompt}') 
        cond1 = len(value.replace(' ', '')) > 0
        attempts += 1
        if cond1:
            if not is_date and not is_email:
                return value
            elif is_date and not is_email:
                try:
                    cond2 = sum([l == '-' for l in value]) == 2
                    cond3 = int(value.split('-')[0]) > 1000 and int(value.split('-')[0]) < 3000
                    cond4 = int(value.split('-')[1]) > 0 and int(value.split('-')[1]) <= 12
                    cond5 = int(value.split('-')[2]) > 0 and int(value.split('-')[2]) <= 31
                    if is_date and cond1 and cond2 and cond3 and cond4 and cond5:
                        return value
                    else: 
                        logging.warning('Date input must be in correct format (YYYY-MM-DD).')    
                except: 
                    logging.warning('Date input must be in correct format (YYYY-MM-DD).')
            elif is_email and not is_date:
                cond6 = sum([l in ['@','.'] for l in value]) == 2
                if cond6:
                    return value
                else: 
                    logging.warning('Must enter full email address.')
        else: 
            logging.warning('Input must contain a value whose length is greater than 0.')  
    sys.exit()




def check_email(email, db_conn, table):
    cur = db_conn.cursor()
    cur.execute(f'''SELECT email FROM {table} WHERE email = '{email}';''')
    query_output = cur.fetchone()
    email_already_exist = 1 if query_output != None else 0
    return email
    







        

        
            







     













attempts = 0
while attempts < 5:
    account_type = input('Select Account Type ( subscriber / subject ): ')
    attempts += 1
    if account_type.lower() not in ['subscriber', 'subject']:
        logging.info('check spelling')
    else: break




cur = conn.cursor()


# subscriber sign-up
if account_type.lower() == 'subscriber':
    # get information
    attempts = 0
    while attempts < 5:
        email = restricted_input('Enter email: ', is_email=True) # < on client-side: don't take '' , case-insensitive >
        query = f'''SELECT email FROM subscribers WHERE email = '{email}';'''
        cur.execute(query)
        query_output = cur.fetchone()
        email_already_exist = 1 if query_output != None else 0
        attempts += 1
        if email_already_exist == 1:
            logging.info('That email is taken, try something different.')
        else:
            break
    if attempts == 5: sys.exit()
    
    
    pwd = restricted_getpass('Enter password: ') # < on client-side: don't take '', double-check >
    first_name = restricted_input('Enter first name: ') # < on client-side: don't take '' , case-insensitive >
    last_name = restricted_input('Enter last name: ') # < on client-side: don't take '' , case-insensitive >
    dob = restricted_input('Enter date of birth (YYYY-MM-DD): ', is_date=True) # < on client-side: don't take '' , '%Y-%m-%d' >
    role = input('Enter role: ')



    #get pwd_id
    logging.info('Inserting password into the database...')
    query = f'''INSERT INTO ss_pwds VALUES (default, '{pwd}') RETURNING id;'''
    cur.execute(query)
    query_output = cur.fetchone()
    pwd_id = query_output[0]
    # < serial number skipping problem > 
    
    logging.info('Inserting user info into the database...')
    query = f'''INSERT INTO subscribers VALUES (default, '{first_name}', '{last_name}', '{email}', '{dob}', '{role}', '{pwd_id}');'''
    cur.execute(query)

    logging.info('Commiting database...')
    conn.commit()



# subject sign-up
else: 
    # get information
    attempts = 0
    while attempts < 5:
        email = restricted_input('Enter email: ', is_email=True) # < on client-side: don't take '' , case-insensitive >
        query = f'''SELECT email FROM subjects WHERE email = '{email}';'''
        cur.execute(query)
        query_output = cur.fetchone()
        email_already_exist = 1 if query_output != None else 0
        attempts += 1
        if email_already_exist == 1:
            logging.info('That email is taken, try something different.')
        else:
            break
    if attempts == 5: sys.exit()
    
    pwd = restricted_getpass('Enter password: ') # < on client-side: don't take '', double-check >
    first_name = restricted_input('Enter first name: ') # < on client-side: don't take '' , case-insensitive >
    last_name = restricted_input('Enter last name: ') # < on client-side: don't take '' , case-insensitive >
    dob = restricted_input('Enter date of birth (YYYY-MM-DD): ', is_date=True) # < on client-side: don't take '' , '%Y-%m-%d' >
    ss_id = input('subscriber ID: ') # < can be filled out later >
    
    #get pwd_id
    query = f'''INSERT INTO sj_pwds VALUES (default, '{pwd}') RETURNING id;'''
    cur.execute(query)
    query_output = cur.fetchone()
    pwd_id = query_output[0]
    
    query = f'''INSERT INTO subjects VALUES (default, '{first_name}', '{last_name}', '{email}', '{dob}', '{ss_id}', '{pwd_id}');'''
    cur.execute(query)

    conn.commit()
    cur.close()
    conn.close()


    # <get token>
    # <link token & account token_id - token.id>
    

    

    



    # with open(f"var/tokens/token{sj_id}, 'r'") as f:
    #     token = json.load(f)
    # uuid = token['uuid']