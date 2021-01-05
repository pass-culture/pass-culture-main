""" config """
from logging import INFO as LOG_LEVEL_INFO
import os
from pathlib import Path

from dotenv import load_dotenv

from .utils import settings as utils


ENV = os.environ.get("ENV", "development")
IS_DEV = ENV == "development"
IS_INTEGRATION = ENV == "integration"
IS_STAGING = ENV == "staging"
IS_PROD = ENV == "production"
IS_TESTING = ENV == "testing"
IS_RUNNING_TESTS = os.environ.get("RUN_ENV") == "tests"

# Load configuration files
env_path = Path(f"./.env.{ENV}")
load_dotenv(dotenv_path=env_path)

if IS_DEV:
    load_dotenv(dotenv_path=".env.local.secret", override=True)
if IS_RUNNING_TESTS:
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
DATABASE_URL = os.environ.get("DATABASE_URL")
DATABASE_URL_TEST = os.environ.get("DATABASE_URL_TEST")
DATABASE_POOL_SIZE = int(os.environ.get("DATABASE_POOL_SIZE", 20))


# FLASK
PROFILE_REQUESTS = bool(os.environ.get("PROFILE_REQUESTS", False))
PROFILE_REQUESTS_LINES_LIMIT = int(os.environ.get("PROFILE_REQUESTS_LINES_LIMIT", 100))
FLASK_PORT = int(os.environ.get("PORT", 5000))
FLASK_SECRET = os.environ.get("FLASK_SECRET", "+%+3Q23!zbc+!Dd@")
CORS_ALLOWED_ORIGIN = os.environ.get("CORS_ALLOWED_ORIGIN")


# REDIS
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")
REDIS_OFFER_IDS_CHUNK_SIZE = int(os.environ.get("REDIS_OFFER_IDS_CHUNK_SIZE", 1000))
REDIS_OFFER_IDS_IN_ERROR_CHUNK_SIZE = int(os.environ.get("REDIS_OFFER_IDS_IN_ERROR_CHUNK_SIZE", 1000))
REDIS_VENUE_IDS_CHUNK_SIZE = int(os.environ.get("REDIS_VENUE_IDS_CHUNK_SIZE", 1000))
REDIS_VENUE_PROVIDERS_CHUNK_SIZE = int(os.environ.get("REDIS_VENUE_PROVIDERS_LRANGE_END", 1))


# SENTRY
SENTRY_DSN = os.environ.get("SENTRY_DSN", "https://0470142cf8d44893be88ecded2a14e42@logs.passculture.app/5")
SENTRY_SAMPLE_RATE = float(os.environ.get("SENTRY_SAMPLE_RATE", 0))

# MAILS
SUPPORT_EMAIL_ADDRESS = os.environ.get("SUPPORT_EMAIL_ADDRESS")
ADMINISTRATION_EMAIL_ADDRESS = os.environ.get("ADMINISTRATION_EMAIL_ADDRESS")
DEV_EMAIL_ADDRESS = os.environ.get("DEV_EMAIL_ADDRESS")
SUPER_ADMIN_EMAIL_ADDRESSES = utils.parse_email_addresses(os.environ.get("SUPER_ADMIN_EMAIL_ADDRESSES"))
ACTIVATION_USER_RECIPIENTS = utils.parse_email_addresses(os.environ.get("ACTIVATION_USER_RECIPIENTS"))
TRANSACTIONS_RECIPIENTS = utils.parse_email_addresses(os.environ.get("TRANSACTIONS_RECIPIENTS"))
PAYMENTS_REPORT_RECIPIENTS = utils.parse_email_addresses(os.environ.get("PAYMENTS_REPORT_RECIPIENTS"))
PAYMENTS_DETAILS_RECIPIENTS = utils.parse_email_addresses(os.environ.get("PAYMENTS_DETAILS_RECIPIENTS"))
WALLET_BALANCES_RECIPIENTS = utils.parse_email_addresses(os.environ.get("WALLET_BALANCES_RECIPIENTS"))

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


# SCALINGO
SCALINGO_APP_TOKEN = os.environ.get("SCALINGO_APP_TOKEN")
SCALINGO_AUTH_URL = "https://auth.scalingo.com/v1"
SCALINGO_API_URL = "https://api.osc-fr1.scalingo.com/v1"
SCALINGO_API_REGION = "osc-fr1"
SCALINGO_API_CONTAINER_SIZE = "L"


# NATIVE APP
NATIVE_ACCOUNT_CREATION_REQUIRES_RECAPTCHA = bool(
    os.environ.get("NATIVE_ACCOUNT_CREATION_REQUIRES_RECAPTCHA", ENV != "testing")
)

# RECAPTCHA
RECAPTCHA_LICENCE_MINIMAL_SCORE = float(os.environ.get("RECAPTCHA_LICENCE_MINIMAL_SCORE", 0.5))
RECAPTCHA_RESET_PASSWORD_MINIMAL_SCORE = float(os.environ.get("RECAPTCHA_RESET_PASSWORD_MINIMAL_SCORE", 0.7))
RECAPTCHA_API_URL = "https://www.google.com/recaptcha/api/siteverify"
RECAPTCHA_SECRET = os.environ.get("RECAPTCHA_SECRET")


# MAILJET
MAILJET_API_KEY = os.environ.get("MAILJET_API_KEY")
MAILJET_API_SECRET = os.environ.get("MAILJET_API_SECRET")
MAILJET_TEMPLATE_DEBUGGING = os.environ.get("MAILJET_TEMPLATE_DEBUGGING", not IS_PROD)
MAILJET_NOT_YET_ELIGIBLE_LIST_ID = os.environ.get("MAILJET_NOT_YET_ELIGIBLE_LIST_ID")


# JWT
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")


# TITELIVE
TITELIVE_FTP_URI = os.environ.get("FTP_TITELIVE_URI")
TITELIVE_FTP_USER = os.environ.get("FTP_TITELIVE_USER")
TITELIVE_FTP_PWD = os.environ.get("FTP_TITELIVE_PWD")


# JOUVE
JOUVE_API_DOMAIN = os.environ.get("JOUVE_API_DOMAIN")
JOUVE_API_USERNAME = os.environ.get("JOUVE_USERNAME")
JOUVE_API_PASSWORD = os.environ.get("JOUVE_PASSWORD")
JOUVE_API_VAULT_GUID = os.environ.get("JOUVE_VAULT_GUID")
JOUVE_APPLICATION_BACKEND = "pcapi.connectors.beneficiaries.jouve_backend.BeneficiaryJouveBackend"


# Test users on staging
STAGING_TEST_USER_PASSWORD = os.environ.get("STAGING_TEST_USER_PASSWORD", "")


# PROVIDERS
ALLOCINE_API_KEY = os.environ.get("ALLOCINE_API_KEY")
FNAC_API_TOKEN = os.environ.get("PROVIDER_FNAC_BASIC_AUTHENTICATION_TOKEN")
PROVIDERS_SYNC_WORKERS_POOL_SIZE = int(os.environ.get("SYNC_WORKERS_POOL_SIZE", 5))


# DEMARCHES SIMPLIFIEES
DMS_OFFERER_PROCEDURE_ID = os.environ.get("DEMARCHES_SIMPLIFIEES_RIB_OFFERER_PROCEDURE_ID")
DMS_VENUE_PROCEDURE_ID = os.environ.get("DEMARCHES_SIMPLIFIEES_RIB_VENUE_PROCEDURE_ID")
DMS_TOKEN = os.environ.get("DEMARCHES_SIMPLIFIEES_TOKEN")
DMS_OLD_ENROLLMENT_PROCEDURE_ID = int(os.environ.get("DEMARCHES_SIMPLIFIEES_ENROLLMENT_PROCEDURE_ID", None))
DMS_NEW_ENROLLMENT_PROCEDURE_ID = int(os.environ.get("DEMARCHES_SIMPLIFIEES_ENROLLMENT_PROCEDURE_ID_v2", None))
DMS_WEBHOOK_TOKEN = os.environ.get("DEMARCHES_SIMPLIFIEES_WEBHOOK_TOKEN")


# SWIFT / OBJECT STORAGE
OBJECT_STORAGE_URL = os.environ.get("OBJECT_STORAGE_URL")
SWIFT_AUTH_URL = os.environ.get("SWIFT_AUTH_URL", "https://auth.cloud.ovh.net/v3/")
SWIFT_BUCKET_NAME = os.environ.get("OVH_BUCKET_NAME")

SWIFT_USER = os.environ.get("OVH_USER")
SWIFT_KEY = os.environ.get("OVH_PASSWORD")
SWIFT_TENANT_NAME = os.environ.get("OVH_TENANT_NAME")
SWIFT_REGION_NAME = os.environ.get("OVH_REGION_NAME", "GRA")

SWIFT_TESTING_USER = os.environ.get("OVH_USER_TESTING")
SWIFT_TESTING_KEY = os.environ.get("OVH_PASSWORD_TESTING")
SWIFT_TESTING_TENANT_NAME = os.environ.get("OVH_TENANT_NAME_TESTING")
SWIFT_TESTING_REGION_NAME = os.environ.get("OVH_REGION_NAME_TESTING", "GRA")
SWIFT_TESTING_URL_PATH = os.environ.get("OVH_URL_PATH_TESTING")

SWIFT_STAGING_USER = os.environ.get("OVH_USER_STAGING")
SWIFT_STAGING_KEY = os.environ.get("OVH_PASSWORD_STAGING")
SWIFT_STAGING_TENANT_NAME = os.environ.get("OVH_TENANT_NAME_STAGING")
SWIFT_STAGING_REGION_NAME = os.environ.get("OVH_REGION_NAME_STAGING", "GRA")
SWIFT_STAGING_URL_PATH = os.environ.get("OVH_URL_PATH_STAGING")

SWIFT_PROD_USER = os.environ.get("OVH_USER_PROD")
SWIFT_PROD_KEY = os.environ.get("OVH_PASSWORD_PROD")
SWIFT_PROD_TENANT_NAME = os.environ.get("OVH_TENANT_NAME_PROD")
SWIFT_PROD_REGION_NAME = os.environ.get("OVH_REGION_NAME_PROD", "GRA")
SWIFT_PROD_URL_PATH = os.environ.get("OVH_URL_PATH_PROD")
