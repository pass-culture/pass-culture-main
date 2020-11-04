""" config """
import os
from logging import INFO as LOG_LEVEL_INFO
from pathlib import Path

API_ROOT_PATH = Path(os.path.dirname(os.path.realpath(__file__))) / '..'
ENV = os.environ.get('ENV', 'development')
IS_DEV = ENV == 'development'
IS_INTEGRATION = ENV == 'integration'
IS_STAGING = ENV == 'staging'
IS_PROD = ENV == 'production'
IS_TESTING = ENV == 'testing'
LOG_LEVEL = int(os.environ.get('LOG_LEVEL', LOG_LEVEL_INFO))
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')

if IS_DEV:
    API_URL = 'http://localhost'
    API_APPLICATION_NAME = None
    WEBAPP_URL = 'http://localhost:3000'
    PRO_URL = 'http://localhost:3001'
    NATIVE_APP_URL = 'passculture://app.passculture.testing'
elif IS_PROD:
    API_URL = 'https://backend.passculture.beta.gouv.fr'
    API_APPLICATION_NAME = 'pass-culture-api'
    WEBAPP_URL = 'https://app.passculture.beta.gouv.fr'
    PRO_URL = 'https://pro.passculture.beta.gouv.fr'
    NATIVE_APP_URL = 'passculture://app.passculture'
elif IS_TESTING:
    API_URL = f'https://backend.passculture-{ENV}.beta.gouv.fr'
    API_APPLICATION_NAME = 'pass-culture-api-dev'
    WEBAPP_URL = f'https://app.passculture-{ENV}.beta.gouv.fr'
    PRO_URL = 'https://pro.testing.passculture.app'
    NATIVE_APP_URL = f'passculture://app.passculture.{ENV}'
else:
    API_URL = f'https://backend.passculture-{ENV}.beta.gouv.fr'
    API_APPLICATION_NAME = f'pass-culture-api-{ENV}'
    WEBAPP_URL = f'https://app.passculture-{ENV}.beta.gouv.fr'
    PRO_URL = f'https://pro.passculture-{ENV}.beta.gouv.fr'
    NATIVE_APP_URL = f'passculture://app.passculture.{ENV}'

BLOB_SIZE = 30
