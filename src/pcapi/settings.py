""" config """
from logging import INFO as LOG_LEVEL_INFO
import os
from pathlib import Path

from dotenv import load_dotenv


ENV = os.environ.get("ENV", "development")
IS_DEV = ENV == "development"
IS_INTEGRATION = ENV == "integration"
IS_STAGING = ENV == "staging"
IS_PROD = ENV == "production"
IS_TESTING = ENV == "testing"


# Load configuration files
env_path = Path(f"./.env.{ENV}")
load_dotenv(dotenv_path=env_path)

if IS_DEV:
    load_dotenv(dotenv_path=".env.local.secret", override=True)
if os.environ.get("RUN_ENV") == "tests":
    load_dotenv(dotenv_path=".env.testauto", override=True)

LOG_LEVEL = int(os.environ.get("LOG_LEVEL", LOG_LEVEL_INFO))


# TODO: move those to .env.{ENV}
if IS_DEV:
    API_URL = "http://localhost"
    API_APPLICATION_NAME = None
    WEBAPP_URL = "http://localhost:3000"
    PRO_URL = "http://localhost:3001"
    NATIVE_APP_URL = "passculture://app.passculture.testing"
elif IS_PROD:
    API_URL = "https://backend.passculture.beta.gouv.fr"
    API_APPLICATION_NAME = "pass-culture-api"
    WEBAPP_URL = "https://app.passculture.beta.gouv.fr"
    PRO_URL = "https://pro.passculture.beta.gouv.fr"
    NATIVE_APP_URL = "passculture://app.passculture"
elif IS_TESTING:
    API_URL = f"https://backend.passculture-{ENV}.beta.gouv.fr"
    API_APPLICATION_NAME = "pass-culture-api-dev"
    WEBAPP_URL = f"https://app.passculture-{ENV}.beta.gouv.fr"
    PRO_URL = f"https://pro.passculture-{ENV}.beta.gouv.fr"
    NATIVE_APP_URL = f"passculture://app.passculture.{ENV}"
else:
    API_URL = f"https://backend.passculture-{ENV}.beta.gouv.fr"
    API_APPLICATION_NAME = f"pass-culture-api-{ENV}"
    WEBAPP_URL = f"https://app.passculture-{ENV}.beta.gouv.fr"
    PRO_URL = f"https://pro.passculture-{ENV}.beta.gouv.fr"
    NATIVE_APP_URL = f"passculture://app.passculture.{ENV}"

BLOB_SIZE = 30


# REDIS
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")
REDIS_OFFER_IDS_CHUNK_SIZE = int(os.environ.get("REDIS_OFFER_IDS_CHUNK_SIZE", 1000))
REDIS_OFFER_IDS_IN_ERROR_CHUNK_SIZE = int(os.environ.get("REDIS_OFFER_IDS_IN_ERROR_CHUNK_SIZE", 1000))
REDIS_VENUE_IDS_CHUNK_SIZE = int(os.environ.get("REDIS_VENUE_IDS_CHUNK_SIZE", 1000))
REDIS_VENUE_PROVIDERS_CHUNK_SIZE = int(os.environ.get("REDIS_VENUE_PROVIDERS_LRANGE_END", 1))
