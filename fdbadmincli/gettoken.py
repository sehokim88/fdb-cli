from const.basic import root
from const import identity, fbclient
import os
import sys
import logging
from getpass import getpass
import time
import random
from selenium.webdriver import Firefox
from selenium.webdriver.support.ui import WebDriverWait















def login(email, password):
    """Login Fitbit User Accounts
    """

    # Open the login page.
    browser = Firefox()
    login_url = f"https://www.fitbit.com/oauth2/authorize?response_type=code&client_id={fbclient.client_id}&redirect_uri=http%3A%2F%2F127.0.0.1%3A5000&scope=sleep%20heartrate&expires_in=604800"
    browser.get(login_url)

    # Type in email ID.
    email_input = WebDriverWait(browser, 5).until(lambda x: x.find_element_by_css_selector('input#ember644'))
    # email_input = browser.find_element_by_css_selector('input#ember653')
    for l in email:
        email_input.send_keys(l)
        time.sleep(random.random()/4)
    time.sleep(1)

    # Type in password.
    password_input = browser.find_element_by_css_selector('input#ember645')
    for l in password:
        password_input.send_keys(l)
        time.sleep(random.random()/3)
    time.sleep(1.2)

    # Click login button.
    browser.find_element_by_css_selector('button#ember685').click()

    # Check AllScope box if not already selected
    try:
        WebDriverWait(browser, 5).until(lambda x: x.find_element_by_css_selector('input#selectAllScope'))
        browser.find_element_by_css_selector('input#selectAllScope').click()
        browser.find_element_by_css_selector('button#allow-button').click()
        time.sleep(5)
    except:
        pass
        
    browser.quit()












class AuthClient:
    """Auth Server that handles Code and Tokens.
    """
    @classmethod    
    def prop(self):
        os.system('netstat -anv | grep 127.0.0.1.5000 > var/ps.txt')
        server_ps = open('var/ps.txt').read()

        if '127.0.0.1.5000' not in server_ps: 
            os.system('python authclient.py &')
            
        else:
            raise Exception
            
    
    @classmethod
    def shut(self):
        os.system('netstat -anv | grep 127.0.0.1.5000 > var/ps.txt')
        server_ps = open('var/ps.txt').read()
        server_pid = server_ps.split(' ')[-7]
        # server_pid = server_ps.replace(" ", "")[-7:-2]
        
        if '127.0.0.1.5000' in server_ps: 
            os.system(f'kill {server_pid}')
            
        else: 
            raise Exception












if __name__ == "__main__":


    if identity.type == 'subject': 
        pass
    else:
        logging.error('Only subject user can get a token.')
        sys.exit()

    # Start the Server
    try: 
        print('> starting the server...')
        AuthClient.prop()
    except: 
        print('> server running')
    time.sleep(3)




    fitbit_email = input('fitbit email: ')
    fitbit_pwd = getpass('fitbit pwd: ')







    try:
        login(fitbit_email, fitbit_pwd)
        
    except: 
        print("> Something went wrong, please try again.")










    # end the server
    try: 
        print('> shutting down the server...')
        AuthClient.shut()
    except: 
        print('> server not found')