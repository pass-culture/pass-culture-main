""" config """
import os
from pathlib import Path

API_ROOT_PATH = Path(os.path.dirname(os.path.realpath(__file__))) / '..'
BROWSER_URL = os.environ.get('BROWSER_URL', 'http://localhost:3000')
DELETE = '_delete_'
ENV = os.environ.get('ENV', 'dev')
IS_DEV = ENV == 'development'
IS_STAGING = ENV == 'staging'

if IS_DEV:
    API_URL = 'localhost'
elif IS_STAGING:
    API_URL = 'https://api.passculture-staging.beta.gouv.fr'
else:
    API_URL = 'https://api.passculture.beta.gouv.fr'

BLOB_SIZE = 80
BLOB_UNREAD_NUMBER = int(BLOB_SIZE/5)
BLOB_READ_NUMBER = int(BLOB_SIZE/5)
