from lib.config import *
from lib.db_conn import conn
from getpass import getpass


# python login.py {account_type} {email} {pwd}



logging.info('Hello, please login to use the service.')






# declare account type
attempts = 0
while attempts < 5:
    account_type = input('Are you a "subscriber" or a "subject"?')
    attempts += 1
    if account_type not in ['subscriber', 'subject']:
        logging.info('Check your spelling and try again.')
    else: 
        break
account_type_verified = 1 if account_type in ['subscriber', 'subject'] else 0





cur = conn.cursor()




# verify email
if account_type_verified == 1:
    attempts = 0
    while attempts < 5:
        email = input('Enter email:   ')
        query = f'''SELECT pwd_id FROM {account_type}s WHERE email = '{email}';'''
        cur.execute(query)
        query_output = cur.fetchone()
        attempts += 1
        if query_output == None:
            logging.info('That email is not in the system, try again.')
        else:
            break
    email_verified = 1 if query_output != None else 0
    if email_verified == 1: password_id = query_output[0]

else: 
    logging.info('Too many failed attempts, please check your account type and try again later.')
    sys.exit()














# verify password
if email_verified == 1:
    account_type_abb = 'ss' if account_type == 'subscriber' else 'sj'
    query = f'''SELECT pwd FROM {account_type_abb}_pwds WHERE id = '{password_id}';'''
    cur.execute(query)
    password_real = cur.fetchone()[0]
    attempts = 0
    while attempts < 5:
        password_input = getpass('Enter password:   ')
        attempts += 1
        if password_input != password_real:
            logging.info('The password does not match with your email, try again.')
        else:
            break
    password_verified = 1 if password_input == password_real else 0

else: 
    logging.info('Too many failed attempts. Check your email and try again later or "/sign_up".')
    sys.exit()










# greeting
if password_verified == 1:
    query = f'''SELECT * FROM {account_type}s WHERE pwd_id = '{password_id}';'''
    cur.execute(query)
    user_cred = cur.fetchone()
    first_name = user_cred[1]
    logging.info(f'Welcome, {first_name.capitalize()}')
    identity = {'account_type_abb' : account_type_abb, 'user_id' : user_cred[0], 'user_name' : user_cred[1]}
    with open(f'{root}/var/identity.json', '+w') as f:
        json.dump(identity, f)
    
    

else: 
    logging.info('Too many failed attempts. Check your password and try again later or "/forgot_password".')
    sys.exit()



cur.close()
conn.close()









