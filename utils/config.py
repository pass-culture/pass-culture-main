""" config """
import os
from logging import INFO as LOG_LEVEL_INFO
from pathlib import Path

API_ROOT_PATH = Path(os.path.dirname(os.path.realpath(__file__))) / '..'
BROWSER_URL = os.environ.get('BROWSER_URL', 'http://localhost:3000')
DELETE = '_delete_'
ENV = os.environ.get('ENV', 'development')
IS_DEV = ENV == 'development'
IS_INTEGRATION = ENV == 'integration'
IS_STAGING = ENV == 'staging'
IS_PROD = ENV == 'production'
LOG_LEVEL = int(os.environ.get('LOG_LEVEL', LOG_LEVEL_INFO))

if IS_DEV:
    API_URL = 'localhost'
elif IS_PROD:
    API_URL = 'https://backend.passculture.beta.gouv.fr'
else:
    API_URL = 'https://backend.passculture-%s.beta.gouv.fr' % ENV

BLOB_SIZE = 10
BLOB_UNREAD_NUMBER = int(BLOB_SIZE/5)
BLOB_READ_NUMBER = int(BLOB_SIZE/5)

ILE_DE_FRANCE_DEPT_CODES = ['75', '78', '91', '94', '93', '95']
