from const.basic import ROOT
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

    logging.debug('> Opening the browser...') # Open the login page.
    browser = Firefox()
    login_url = f"https://www.fitbit.com/oauth2/authorize?response_type=code&client_id={fbclient.CLIENT_ID}&redirect_uri=http%3A%2F%2F127.0.0.1%3A5000&scope=sleep%20heartrate&expires_in=604800"
    logging.debug('> Accessing the URL...')
    browser.get(login_url)

    logging.debug('> Typing the email ID...') # Type in email ID.
    email_input = WebDriverWait(browser, 5).until(lambda x: x.find_element_by_css_selector('input#ember644'))
    # email_input = browser.find_element_by_css_selector('input#ember653')
    for l in email:
        email_input.send_keys(l)
        time.sleep(random.random()/4)
    time.sleep(1)

    logging.debug('> Typing the password...') # Type in password.
    password_input = browser.find_element_by_css_selector('input#ember645')
    for l in password:
        password_input.send_keys(l)
        time.sleep(random.random()/3)
    time.sleep(1.2)

    logging.debug('> Clicking the login button...') # Click login button.
    browser.find_element_by_css_selector('button#ember685').click()

    logging.debug('> Selecting Permission Scope boxes...') # Check AllScope box if not already selected
    try:
        WebDriverWait(browser, 5).until(lambda x: x.find_element_by_css_selector('input#selectAllScope'))
        browser.find_element_by_css_selector('input#selectAllScope').click()
        browser.find_element_by_css_selector('button#allow-button').click()
        time.sleep(5)
    except:
        pass
        
    logging.debug('> Shutting the browser...')
    browser.quit()












class AuthClientToggle:
    """AuthClient server manager.
    """
    @classmethod    
    def prop(cls):
        os.system(f'netstat -anv | grep 127.0.0.1.5000 > {ROOT}/var/authclient.pid')
        server_ps = open(f'{ROOT}/var/authclient.pid').read()

        if '127.0.0.1.5000' not in server_ps: 
            logging.debug('> Starting the server...')
            os.system('python authclient.py &')
            
        else:
            logging.debug('> Server already running...')

    
    @classmethod
    def shut(cls):
        os.system(f'netstat -anv | grep 127.0.0.1.5000 > {ROOT}/var/authclient.pid')
        server_ps = open(f'{ROOT}/var/authclient.pid').read()
        server_pid = server_ps.split(' ')[-7]
        
        if '127.0.0.1.5000' in server_ps: 
            logging.debug('> Shutting the server...')
            os.system(f'kill {server_pid}')
            
            












if __name__ == "__main__":


    # Check the User's Account type
    if identity.TYPE == 'subject': 
        pass
    else:
        logging.error('Only subject user can get a token.')
        sys.exit()

    # Start the Server
    logging.info('> Starting the server...')
    AuthClientToggle.prop()
    time.sleep(3)


    # Get creds
    fitbit_email = input('fitbit email: ')
    fitbit_pwd = getpass('fitbit pwd: ')


    # Get token
    try:
        logging.info('> Logging in...')
        login(fitbit_email, fitbit_pwd)
        
    except: 
        logging.info("> Something went wrong, please try again.")


    # end the server
    logging.info('> Shutting down the server...')
    AuthClientToggle.shut()