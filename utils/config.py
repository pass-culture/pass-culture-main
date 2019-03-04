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

BLOB_SIZE = 80
BLOB_UNREAD_NUMBER = int(BLOB_SIZE / 5)
BLOB_READ_NUMBER = int(BLOB_SIZE / 5)

DEPT_CODE_VISIBILITY = {'93': ['75', '77', '78', '91', '92', '93', '94', '95'],
                        '29': ['22', '25', '29', '56'],
                        '67': ['54', '55', '57', '67', '68', '88'],
                        '34': ['11', '12', '30', '34', '48', '81'],
                        '97': ['97', '971', '972', '973']}
ILE_DE_FRANCE_DEPT_CODES = ['75', '77', '78', '91', '92', '93', '94', '95']
