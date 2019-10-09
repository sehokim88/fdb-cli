from lib.config import *
from lib.db_conn import conn
from getpass import getpass
from datetime import datetime
import string





class SignUpForm:
    def __init__(self, db_conn):
        self.db_conn = db_conn
        self.type = None
        self.email = None
        self.pwd = None
        self.first_name = None
        self.last_name = None
        self.dob = None
        self.role = None
        self.ss_id = None





    def get_type(self, prompt):
        attempts = 0
        while attempts < 5:
            value = input(prompt)
            attempts += 1
            if value.lower() in ['subscriber', 'subject']:
                self.type = value
                break
            else: 
                logging.error('Must select from the option.')
        if attempts == 5: sys.exit()




    def get_email(self, prompt):
        attempts = 0
        while attempts < 5:
            value = input(f'{prompt}')
            cond1 = len(value.replace(' ', '')) > 0
            cond2 = sum([l in ['@','.'] for l in value]) == 2
            attempts += 1
            if not cond1:
                logging.error('Input must contain a value whose length is greater than 0.')
            elif not cond2:
                logging.error('Must enter a full email address.')
            elif cond1 and cond2:
                email_avail = self._check_email(value)
                if email_avail:
                    self.email = value
                    break
                else:
                    logging.error('That email is already taken.')
        if attempts == 5: sys.exit()



    def get_pwd(self, prompt):
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
                        logging.error('Password must contain at least one letter and one digit and longer than 6 letter-digit combinations.')
                if attempts == 5: sys.exit()
            retype_attempts += 1
            if values[0] == values[1]: 
                self.pwd = values[0]
                break
            else: 
                logging.error('Two passwords do not match, try again.')
        if retype_attempts == 5: sys.exit()




    def get_value(self, prompt, key):
        if key in ['first_name', 'last_name', 'role', 'ss_id']:
            pass
        else: 
            raise ValueError('Invalid Key.')
            
        attempts = 0
        while attempts < 5:
            value = input(f'{prompt}') 
            cond1 = len(value.replace(' ', '')) > 0
            attempts += 1
            if cond1:
                if key == 'first_name': self.first_name = value
                elif key == 'last_name': self.last_name = value
                elif key == 'role': self.role = value
                elif key == 'ss_id': self.ss_id = value
                break
                    
            else: 
                logging.error('Input must contain a value whose length is greater than 0.')  
        if attempts == 5: sys.exit()

    

    def get_date_value(self, prompt, key):
        if key in ['dob']:
            pass
        else:
            raise ValueError('Invalid Key.')

        attempts = 0
        while attempts < 5:
            value = input(f'{prompt}')
            cond1 = len(value.replace(' ', '')) > 0
            cond2 = sum([l == '-' for l in value]) == 2
            attempts += 1
            try:
                cond3 = int(value.split('-')[0]) > 1000 and int(value.split('-')[0]) < 3000
                cond4 = int(value.split('-')[1]) > 0 and int(value.split('-')[1]) <= 12
                cond5 = int(value.split('-')[2]) > 0 and int(value.split('-')[2]) <= 31  
            except: 
                logging.error('Date input must be in correct format (YYYY-MM-DD).')
            else: 
                if cond1 and cond2 and cond3 and cond4 and cond5:
                    self.dob = value
                    break
                else: 
                    logging.error('Date input must be in correct format (YYYY-MM-DD).')  
        if attempts == 5: sys.exit()




    def _check_email(self, email):
        cur = self.db_conn.cursor()
        cur.execute(f'''SELECT email FROM {self.type}s WHERE email = '{email}';''')
        email_avail = 0 if cur.fetchone() != None else 1
        return email_avail




    def _check_form(self):
        if None not in [self.email, self.pwd, self.first_name, self.last_name, self.dob]:
            return 1
        else: 
            return 0
    



    def submit(self):
        if self._check_form():
            pass
        else: 
            logging.error('submit the form after filling out.')
            sys.exit()

        cur = self.db_conn.cursor()
        logging.info('Submitting the Form...')

        if self.type == 'subject':
            
            logging.debug('Inserting passwords into the database...')
            cur.execute(f'''INSERT INTO sj_pwds VALUES (default, '{self.pwd}') RETURNING id;''')
            pwd_id = cur.fetchone()[0]

            logging.debug('Inserting user info into the database...')
            cur.execute(f'''INSERT INTO subjects VALUES (
                            default, 
                            '{self.first_name}', 
                            '{self.last_name}', 
                            '{self.email}', 
                            '{self.dob}', 
                            {self.ss_id}, 
                            {pwd_id})
                            ;''')

        else: 

            logging.debug('Inserting passwords into the database...')
            cur.execute(f'''INSERT INTO ss_pwds VALUES (default, '{self.pwd}') RETURNING id;''')
            pwd_id = cur.fetchone()[0]

            if self.role == 'null':
                role_id = 'null'
            else: 
                logging.debug('Checking if role exist in the database...')
                cur.execute(f'''SELECT id FROM roles WHERE role = '{self.role}';''')
                role_exist = 1 if cur.fetchone() != None else 0
                if role_exist: 
                    logging.debug('Role already exist in the DB.')
                    role_id = cur.fetchone()[0]
                else:
                    logging.debug('Role does not exist in the DB, inserting now...')
                    cur.execute(f'''INSERT INTO roles VALUES (default, '{self.role}') RETURNING id;''')
                    role_id = cur.fetchone()[0]

            logging.debug('Inserting user info into the database...')
            cur.execute(f'''INSERT INTO subscribers VALUES (
                            default, 
                            '{self.first_name}', 
                            '{self.last_name}', 
                            '{self.email}', 
                            '{self.dob}', 
                            {role_id}, 
                            {pwd_id})
                            ;''')


        

if __name__ == '__main__':


    form = SignUpForm(conn)

    form.get_type('type (subject or subscriber): ')
    if form.type == 'subject':
        form.get_email('email: ')
        form.get_pwd('pwd: ')
        form.get_value('first_name: ', 'first_name')
        form.get_value('last_name: ', 'last_name')
        form.get_date_value('dob: ', 'dob')
        form.get_value('subscriber ID (type "null" if not applicable): ', 'ss_id')

    else:
        form.get_email('email: ')
        form.get_pwd('pwd: ')
        form.get_value('first_name: ', 'first_name')
        form.get_value('last_name: ', 'last_name')
        form.get_date_value('dob: ', 'dob')
        form.get_value('role (type "null" if not applicable): ', 'role')

    form.submit()
    logging.debug('Commit and Close DB...')
    conn.commit()
    conn.close()



