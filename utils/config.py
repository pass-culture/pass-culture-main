""" config """
import os

BROWSER_URL = os.environ.get('BROWSER_URL', 'http://localhost:3000')
DELETE = '_delete_'
ENV = os.environ.get('ENV', 'dev')
IS_DEV = ENV == 'development'
IS_STAGING = ENV == 'staging'

BLOB_SIZE = 80
BLOB_UNREAD_NUMBER = int(BLOB_SIZE/5)
BLOB_READ_NUMBER = int(BLOB_SIZE/5)
