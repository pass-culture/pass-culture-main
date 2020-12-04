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


# DATABASE
DB_MIGRATION_LOCK_TIMEOUT = int(os.environ.get("DB_MIGRATION_STATEMENT_TIMEOUT", 5000))
DB_MIGRATION_STATEMENT_TIMEOUT = int(os.environ.get("DB_MIGRATION_STATEMENT_TIMEOUT", 60000))


# REDIS
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")
REDIS_OFFER_IDS_CHUNK_SIZE = int(os.environ.get("REDIS_OFFER_IDS_CHUNK_SIZE", 1000))
REDIS_OFFER_IDS_IN_ERROR_CHUNK_SIZE = int(os.environ.get("REDIS_OFFER_IDS_IN_ERROR_CHUNK_SIZE", 1000))
REDIS_VENUE_IDS_CHUNK_SIZE = int(os.environ.get("REDIS_VENUE_IDS_CHUNK_SIZE", 1000))
REDIS_VENUE_PROVIDERS_CHUNK_SIZE = int(os.environ.get("REDIS_VENUE_PROVIDERS_LRANGE_END", 1))


# MAILS
# Temporary setting to allow load tests to disable sending email
# Possible values:
#   - mailjet
#   - log
SEND_RAW_EMAIL_BACKEND = os.environ.get("SEND_RAW_EMAIL_BACKEND", "mailjet").lower()


# ALGOLIA
ALGOLIA_API_KEY = os.environ.get("ALGOLIA_API_KEY")
ALGOLIA_APPLICATION_ID = os.environ.get("ALGOLIA_APPLICATION_ID")
ALGOLIA_INDEX_NAME = os.environ.get("ALGOLIA_INDEX_NAME")
ALGOLIA_TRIGGER_INDEXATION = bool(int(os.environ.get("ALGOLIA_TRIGGER_INDEXATION", "0")))
ALGOLIA_CRON_INDEXING_OFFERS_BY_OFFER_FREQUENCY = os.environ.get("ALGOLIA_CRON_INDEXING_OFFERS_BY_OFFER_FREQUENCY", "*")
ALGOLIA_CRON_INDEXING_OFFERS_BY_VENUE_FREQUENCY = os.environ.get(
    "ALGOLIA_CRON_INDEXING_OFFERS_BY_VENUE_FREQUENCY", "10"
)
ALGOLIA_CRON_INDEXING_OFFERS_BY_VENUE_PROVIDER_FREQUENCY = os.environ.get(
    "ALGOLIA_CRON_INDEXING_OFFERS_BY_VENUE_PROVIDER_FREQUENCY", "10"
)
ALGOLIA_CRON_INDEXING_OFFERS_IN_ERROR_BY_OFFER_FREQUENCY = os.environ.get(
    "ALGOLIA_CRON_INDEXING_OFFERS_IN_ERROR_BY_OFFER_FREQUENCY", "10"
)
ALGOLIA_DELETING_OFFERS_CHUNK_SIZE = int(os.environ.get("ALGOLIA_DELETING_OFFERS_CHUNK_SIZE", 10000))
ALGOLIA_OFFERS_BY_VENUE_CHUNK_SIZE = int(os.environ.get("ALGOLIA_OFFERS_BY_VENUE_CHUNK_SIZE", 10000))
ALGOLIA_OFFERS_BY_VENUE_PROVIDER_CHUNK_SIZE = int(os.environ.get("ALGOLIA_OFFERS_BY_VENUE_PROVIDER_CHUNK_SIZE", 10000))
ALGOLIA_SYNC_WORKERS_POOL_SIZE = int(os.environ.get("ALGOLIA_SYNC_WORKERS_POOL_SIZE", 10))


# NATIVE APP
NATIVE_ACCOUNT_CREATION_REQUIRES_RECAPTCHA = bool(
    os.environ.get("NATIVE_ACCOUNT_CREATION_REQUIRES_RECAPTCHA", ENV != "testing")
)

# RECAPTCHA
RECAPTCHA_LICENCE_MINIMAL_SCORE = float(os.environ.get("RECAPTCHA_LICENCE_MINIMAL_SCORE", 0.5))
RECAPTCHA_RESET_PASSWORD_MINIMAL_SCORE = float(os.environ.get("RECAPTCHA_RESET_PASSWORD_MINIMAL_SCORE", 0.7))
