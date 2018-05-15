import os

BROWSER_URL = os.environ.get('BROWSER_URL', 'http://localhost:3000')
ENV = os.environ.get('ENV', 'dev') or 'dev'
print('ENV', ENV)
IS_DEV = ENV == 'dev'
IS_STAGING = ENV == 'staging'

BEFORE_AFTER_LIMIT = 5
BLOB_SIZE = 80
