import os

BROWSER_URL = os.environ.get('BROWSER_URL', 'http://localhost:3000')
ENV = os.environ.get('ENV', 'dev')
IS_DEV = ENV == 'dev'

BLOB_LIMIT = 10
RECO_LIMIT = 20
