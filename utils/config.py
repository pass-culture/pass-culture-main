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
IS_TESTING = ENV == 'testing'
LOG_LEVEL = int(os.environ.get('LOG_LEVEL', LOG_LEVEL_INFO))

if IS_DEV:
    API_URL = 'http://localhost'
    WEBAPP_URL = 'http://localhost:3000'
    PRO_URL = 'http://localhost:3001'
elif IS_PROD:
    API_URL = 'https://backend.passculture.beta.gouv.fr'
    WEBAPP_URL = 'https://app.passculture.beta.gouv.fr'
    PRO_URL = 'https://pro.passculture.beta.gouv.fr'
else:
    API_URL = 'https://backend.passculture-%s.beta.gouv.fr' % ENV
    WEBAPP_URL = 'https://app.passculture-%s.beta.gouv.fr' % ENV
    PRO_URL = 'https://pro.passculture-%s.beta.gouv.fr' % ENV

BLOB_SIZE = 30
