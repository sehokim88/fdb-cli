import os

os.environ['TEST'] = '1'
print(os.environ['TEST'])
print(os.environ.get('TEST'))