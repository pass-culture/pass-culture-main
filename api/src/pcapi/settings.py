""" config """
import base64
import json
from logging import INFO as LOG_LEVEL_INFO
import os
from pathlib import Path

from dotenv import load_dotenv
import semver

from .utils import secrets as secrets_utils
from .utils import settings as utils
from .utils.example_certificate import PRIVATE_KEY_EXAMPLE
from .utils.example_certificate import PUBLIC_CERTIFICATE_EXAMPLE


ENV = os.environ.get("ENV", "development")
IS_DEV = ENV == "development"
IS_INTEGRATION = ENV == "integration"
IS_STAGING = ENV == "staging"
IS_PROD = ENV == "production"
IS_TESTING = ENV == "testing"
IS_RUNNING_TESTS = os.environ.get("RUN_ENV") == "tests"
IS_PERFORMANCE_TESTS = bool(os.environ.get("IS_PERFORMANCE_TESTS", False))
assert not (IS_PROD and IS_PERFORMANCE_TESTS)

# Load configuration files
env_path = Path(f"./.env.{ENV}")
load_dotenv(dotenv_path=env_path)

if IS_DEV:
    load_dotenv(dotenv_path=".env.local.secret", override=True)
if IS_RUNNING_TESTS:
    load_dotenv(dotenv_path=".env.testauto", override=True)

LOG_LEVEL = int(os.environ.get("LOG_LEVEL", LOG_LEVEL_INFO))


# Default backends
if IS_PROD or IS_INTEGRATION:
    _default_search_backend = "pcapi.core.search.backends.algolia.AlgoliaBackend"
    _default_email_backend = "pcapi.core.mails.backends.sendinblue.SendinblueBackend"
    _default_google_drive_backend = "pcapi.connectors.googledrive.GoogleDriveBackend"
    _default_internal_notification_backend = "pcapi.notifications.internal.backends.slack.SlackBackend"
    _default_push_notification_backend = "pcapi.notifications.push.backends.batch.BatchBackend"
    _default_sms_notification_backend = "pcapi.notifications.sms.backends.sendinblue.SendinblueBackend"
    _default_object_storage_provider = None  # it must be explicitly set
    _default_sirene_backend = "pcapi.connectors.sirene.InseeBackend"
elif IS_STAGING or IS_TESTING:
    _default_search_backend = "pcapi.core.search.backends.algolia.AlgoliaBackend"
    _default_email_backend = "pcapi.core.mails.backends.sendinblue.ToDevSendinblueBackend"
    _default_google_drive_backend = "pcapi.connectors.googledrive.GoogleDriveBackend"
    _default_internal_notification_backend = "pcapi.notifications.internal.backends.slack.SlackBackend"
    _default_push_notification_backend = "pcapi.notifications.push.backends.batch.BatchBackend"
    _default_sms_notification_backend = "pcapi.notifications.sms.backends.sendinblue.ToDevSendinblueBackend"
    _default_object_storage_provider = None  # it must be explicitly set
    _default_sirene_backend = "pcapi.connectors.sirene.InseeBackend"
elif IS_RUNNING_TESTS:
    _default_search_backend = "pcapi.core.search.backends.testing.TestingBackend"
    _default_email_backend = "pcapi.core.mails.backends.testing.TestingBackend"
    _default_google_drive_backend = "pcapi.connectors.googledrive.TestingBackend"
    _default_internal_notification_backend = "pcapi.notifications.internal.backends.testing.TestingBackend"
    _default_push_notification_backend = "pcapi.notifications.push.backends.testing.TestingBackend"
    _default_sms_notification_backend = "pcapi.notifications.sms.backends.testing.TestingBackend"
    _default_object_storage_provider = "local"
    _default_sirene_backend = "pcapi.connectors.sirene.TestingBackend"
elif IS_DEV:
    _default_search_backend = "pcapi.core.search.backends.testing.TestingBackend"
    _default_email_backend = "pcapi.core.mails.backends.logger.LoggerBackend"
    _default_google_drive_backend = "pcapi.connectors.googledrive.TestingBackend"
    _default_internal_notification_backend = "pcapi.notifications.internal.backends.logger.LoggerBackend"
    _default_push_notification_backend = "pcapi.notifications.push.backends.logger.LoggerBackend"
    _default_sms_notification_backend = "pcapi.notifications.sms.backends.logger.LoggerBackend"
    _default_object_storage_provider = "local"
    _default_sirene_backend = "pcapi.connectors.sirene.TestingBackend"
else:
    raise RuntimeError("Unknown environment")


# API config
API_URL = os.environ.get("API_URL")


# Applications urls
WEBAPP_V2_URL = os.environ.get("WEBAPP_V2_URL")
WEBAPP_V2_REDIRECT_URL = os.environ.get("WEBAPP_V2_REDIRECT_URL")
PRO_URL = os.environ.get("PRO_URL")
FIREBASE_DYNAMIC_LINKS_URL = os.environ.get("FIREBASE_DYNAMIC_LINKS_URL")


# DATABASE
DB_MIGRATION_LOCK_TIMEOUT = int(os.environ.get("DB_MIGRATION_LOCK_TIMEOUT", 5000))
DB_MIGRATION_STATEMENT_TIMEOUT = int(os.environ.get("DB_MIGRATION_STATEMENT_TIMEOUT", 60000))
DATABASE_URL = secrets_utils.get("DATABASE_URL") if not IS_RUNNING_TESTS else os.environ.get("DATABASE_URL_TEST")
DATABASE_POOL_SIZE = int(os.environ.get("DATABASE_POOL_SIZE", 20))
DATABASE_STATEMENT_TIMEOUT = int(os.environ.get("DATABASE_STATEMENT_TIMEOUT", 0))
DATABASE_LOCK_TIMEOUT = int(os.environ.get("DATABASE_LOCK_TIMEOUT", 0))
DATABASE_IDLE_IN_TRANSACTION_SESSION_TIMEOUT = int(os.environ.get("DATABASE_IDLE_IN_TRANSACTION_SESSION_TIMEOUT", 0))
SQLALCHEMY_ECHO = bool(int(os.environ.get("SQLALCHEMY_ECHO", "0")))

# FLASK
PROFILE_REQUESTS = bool(os.environ.get("PROFILE_REQUESTS", False))
PROFILE_REQUESTS_LINES_LIMIT = int(os.environ.get("PROFILE_REQUESTS_LINES_LIMIT", 100))
FLASK_PORT = int(os.environ.get("PORT", 5001))
FLASK_SECRET = secrets_utils.get("FLASK_SECRET", "+%+3Q23!zbc+!Dd@")
CORS_ALLOWED_ORIGINS = os.environ["CORS_ALLOWED_ORIGINS"].split(",")
CORS_ALLOWED_ORIGINS_BACKOFFICE = os.environ["CORS_ALLOWED_ORIGINS_BACKOFFICE"].split(",")
CORS_ALLOWED_ORIGINS_NATIVE = os.environ["CORS_ALLOWED_ORIGINS_NATIVE"].split(",")
CORS_ALLOWED_ORIGINS_ADAGE_IFRAME = os.environ["CORS_ALLOWED_ORIGINS_ADAGE_IFRAME"].split(",")

# NATIVE APP SPECIFIC SETTINGS
NATIVE_APP_MINIMAL_CLIENT_VERSION = semver.VersionInfo.parse(
    os.environ.get("NATIVE_APP_MINIMAL_CLIENT_VERSION", "1.132.1")
)


# REDIS
REDIS_URL = secrets_utils.get("REDIS_URL", "redis://localhost:6379")
REDIS_OFFER_IDS_CHUNK_SIZE = int(os.environ.get("REDIS_OFFER_IDS_CHUNK_SIZE", 1000))
REDIS_COLLECTIVE_OFFER_IDS_CHUNK_SIZE = int(os.environ.get("REDIS_COLLECTIVE_OFFER_IDS_CHUNK_SIZE", 1000))
REDIS_COLLECTIVE_OFFER_TEMPLATE_IDS_CHUNK_SIZE = int(
    os.environ.get("REDIS_COLLECTIVE_OFFER_TEMPLATE_IDS_CHUNK_SIZE", 1000)
)
REDIS_VENUE_IDS_FOR_OFFERS_CHUNK_SIZE = int(os.environ.get("REDIS_VENUE_IDS_FOR_OFFERS_CHUNK_SIZE", 1000))
REDIS_VENUE_IDS_CHUNK_SIZE = int(os.environ.get("REDIS_VENUE_IDS_CHUNK_SIZE", 1000))


# SENTRY
SENTRY_DSN = secrets_utils.get("SENTRY_DSN", "")
SENTRY_SAMPLE_RATE = float(os.environ.get("SENTRY_SAMPLE_RATE", 0))


# USERS
MAX_FAVORITES = int(os.environ.get("MAX_FAVORITES", 100))  # 0 is unlimited
MAX_API_KEY_PER_OFFERER = int(os.environ.get("MAX_API_KEY_PER_OFFERER", 5))


# MAIL
ADMINISTRATION_EMAIL_ADDRESS = secrets_utils.get("ADMINISTRATION_EMAIL_ADDRESS")
COMPLIANCE_EMAIL_ADDRESS = secrets_utils.get("COMPLIANCE_EMAIL_ADDRESS", "")
DEV_EMAIL_ADDRESS = secrets_utils.get("DEV_EMAIL_ADDRESS")

# When load testing, override `EMAIL_BACKEND` to avoid going over SendinBlue quota:
#     EMAIL_BACKEND="pcapi.core.mails.backends.logger.LoggerBackend"
EMAIL_BACKEND = os.environ.get("EMAIL_BACKEND", _default_email_backend)

REPORT_OFFER_EMAIL_ADDRESS = secrets_utils.get("REPORT_OFFER_EMAIL_ADDRESS", "")
SUPER_ADMIN_EMAIL_ADDRESSES = utils.parse_str_to_list(secrets_utils.get("SUPER_ADMIN_EMAIL_ADDRESSES"))
SUPPORT_EMAIL_ADDRESS = secrets_utils.get("SUPPORT_EMAIL_ADDRESS", "")
SUPPORT_PRO_EMAIL_ADDRESS = secrets_utils.get("SUPPORT_PRO_EMAIL_ADDRESS", "")
WHITELISTED_EMAIL_RECIPIENTS = utils.parse_str_to_list(secrets_utils.get("WHITELISTED_EMAIL_RECIPIENTS"))
WHITELISTED_SMS_RECIPIENTS = utils.parse_phone_numbers(secrets_utils.get("WHITELISTED_SMS_RECIPIENTS"))

# NOTIFICATIONS
INTERNAL_NOTIFICATION_BACKEND = os.environ.get("INTERNAL_NOTIFICATION_BACKEND", _default_internal_notification_backend)
PUSH_NOTIFICATION_BACKEND = os.environ.get("PUSH_NOTIFICATION_BACKEND", _default_push_notification_backend)
SMS_NOTIFICATION_BACKEND = os.environ.get("SMS_NOTIFICATION_BACKEND", _default_sms_notification_backend)

MAX_SMS_SENT_FOR_PHONE_VALIDATION = int(os.environ.get("MAX_SMS_SENT_FOR_PHONE_VALIDATION", 3))
MAX_PHONE_VALIDATION_ATTEMPTS = int(os.environ.get("MAX_PHONE_VALIDATION_ATTEMPTS", 3))

SENT_SMS_COUNTER_TTL = int(os.environ.get("SENT_SMS_COUNTER_TTL", 12 * 60 * 60))
PHONE_VALIDATION_ATTEMPTS_TTL = int(os.environ.get("PHONE_VALIDATION_ATTEMPTS_TTL", 30 * 24 * 60 * 60))

# ALGOLIA
ALGOLIA_API_KEY = secrets_utils.get("ALGOLIA_API_KEY", "dummy-key")
ALGOLIA_APPLICATION_ID = secrets_utils.get("ALGOLIA_APPLICATION_ID", "dummy-app-id")
ALGOLIA_OFFERS_INDEX_NAME = os.environ.get("ALGOLIA_OFFERS_INDEX_NAME")
ALGOLIA_COLLECTIVE_OFFERS_INDEX_NAME = os.environ.get("ALGOLIA_COLLECTIVE_OFFERS_INDEX_NAME")
ALGOLIA_COLLECTIVE_OFFERS_TEMPLATES_INDEX_NAME = os.environ.get("ALGOLIA_COLLECTIVE_OFFERS_TEMPLATES_INDEX_NAME")
ALGOLIA_VENUES_INDEX_NAME = os.environ.get("ALGOLIA_VENUES_INDEX_NAME")
ALGOLIA_TRIGGER_INDEXATION = bool(int(os.environ.get("ALGOLIA_TRIGGER_INDEXATION", "0")))
ALGOLIA_CRON_INDEXING_OFFERS_BY_OFFER_FREQUENCY = os.environ.get("ALGOLIA_CRON_INDEXING_OFFERS_BY_OFFER_FREQUENCY", "*")
ALGOLIA_CRON_INDEXING_OFFERS_BY_VENUE_PROVIDER_FREQUENCY = os.environ.get(
    "ALGOLIA_CRON_INDEXING_OFFERS_BY_VENUE_PROVIDER_FREQUENCY", "10"
)
ALGOLIA_CRON_INDEXING_OFFERS_IN_ERROR_BY_OFFER_FREQUENCY = os.environ.get(
    "ALGOLIA_CRON_INDEXING_OFFERS_IN_ERROR_BY_OFFER_FREQUENCY", "25"
)

CRON_INDEXING_VENUES_FREQUENCY = os.environ.get("CRON_INDEXING_VENUES_FREQUENCY", "40")
CRON_INDEXING_COLLECTIVE_OFFERS_FREQUENCY = os.environ.get("CRON_INDEXING_COLLECTIVE_OFFERS_FREQUENCY", "*")
CRON_INDEXING_COLLECTIVE_OFFERS_TEMPLATES_FREQUENCY = os.environ.get(
    "CRON_INDEXING_COLLECTIVE_OFFERS_TEMPLATES_FREQUENCY", "*"
)

CRON_INDEXING_VENUES_IN_ERROR_FREQUENCY = os.environ.get("CRON_INDEXING_VENUES_IN_ERROR_FREQUENCY", "55")
CRON_INDEXING_COLLECTIVE_OFFERS_IN_ERROR_FREQUENCY = os.environ.get(
    "CRON_INDEXING_COLLECTIVE_OFFERS_IN_ERROR_FREQUENCY", "30"
)
CRON_INDEXING_COLLECTIVE_OFFERS_TEMPLATES_IN_ERROR_FREQUENCY = os.environ.get(
    "CRON_INDEXING_COLLECTIVE_OFFERS_TEMPLATES_IN_ERROR_FREQUENCY", "35"
)

ALGOLIA_DELETING_OFFERS_CHUNK_SIZE = int(os.environ.get("ALGOLIA_DELETING_OFFERS_CHUNK_SIZE", 10000))
ALGOLIA_DELETING_COLLECTIVE_OFFERS_CHUNK_SIZE = int(
    os.environ.get("ALGOLIA_DELETING_COLLECTIVE_OFFERS_CHUNK_SIZE", 10000)
)
ALGOLIA_OFFERS_BY_VENUE_CHUNK_SIZE = int(os.environ.get("ALGOLIA_OFFERS_BY_VENUE_CHUNK_SIZE", 10000))

# BATCH
BATCH_API_URL = os.environ.get("BATCH_API_URL", "https://api.batch.com")
BATCH_ANDROID_API_KEY = os.environ.get("BATCH_ANDROID_API_KEY", "")
BATCH_IOS_API_KEY = os.environ.get("BATCH_IOS_API_KEY", "")
BATCH_SECRET_API_KEY = secrets_utils.get("BATCH_SECRET_API_KEY", "")

# SENDINBLUE
SENDINBLUE_API_KEY = secrets_utils.get("SENDINBLUE_API_KEY", "")
SENDINBLUE_PRO_CONTACT_LIST_ID = int(os.environ.get("SENDINBLUE_PRO_CONTACT_LIST_ID", 12))
SENDINBLUE_YOUNG_CONTACT_LIST_ID = int(os.environ.get("SENDINBLUE_YOUNG_CONTACT_LIST_ID", 4))
SENDINBLUE_AUTOMATION_YOUNG_18_IN_1_MONTH_LIST_ID = int(
    os.environ.get("SENDINBLUE_AUTOMATION_YOUNG_18_IN_1_MONTH_LIST_ID", 22)
)
SENDINBLUE_AUTOMATION_YOUNG_INACTIVE_30_DAYS_LIST_ID = int(
    os.environ.get("SENDINBLUE_AUTOMATION_YOUNG_INACTIVE_30_DAYS_LIST_ID", 20)
)
SENDINBLUE_AUTOMATION_YOUNG_1_YEAR_WITH_PASS_LIST_ID = int(
    os.environ.get("SENDINBLUE_AUTOMATION_YOUNG_1_YEAR_WITH_PASS_LIST_ID", 21)
)
SENDINBLUE_AUTOMATION_YOUNG_EXPIRATION_M3_ID = int(os.environ.get("SENDINBLUE_AUTOMATION_YOUNG_EXPIRATION_M3_ID", 23))
SENDINBLUE_AUTOMATION_YOUNG_EX_BENEFICIARY_ID = int(os.environ.get("SENDINBLUE_AUTOMATION_YOUNG_EX_BENEFICIARY_ID", 24))

# RECAPTCHA
RECAPTCHA_RESET_PASSWORD_MINIMAL_SCORE = float(os.environ.get("RECAPTCHA_RESET_PASSWORD_MINIMAL_SCORE", 0.7))
RECAPTCHA_API_URL = "https://www.google.com/recaptcha/api/siteverify"
RECAPTCHA_SECRET = secrets_utils.get("RECAPTCHA_SECRET")
NATIVE_RECAPTCHA_SECRET = secrets_utils.get("NATIVE_RECAPTCHA_SECRET")


# JWT
JWT_SECRET_KEY = secrets_utils.get("JWT_SECRET_KEY")
# default is 15 minutes
# https://flask-jwt-extended.readthedocs.io/en/stable/options/#JWT_ACCESS_TOKEN_EXPIRES
JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES", 60 * 15))


# TITELIVE
TITELIVE_FTP_URI = secrets_utils.get("FTP_TITELIVE_URI")
TITELIVE_FTP_USER = secrets_utils.get("FTP_TITELIVE_USER")
TITELIVE_FTP_PWD = secrets_utils.get("FTP_TITELIVE_PWD")

# UBBLE
UBBLE_API_URL = os.environ.get("UBBLE_API_URL", "https://api.ubble.ai")
UBBLE_CLIENT_ID = secrets_utils.get("UBBLE_CLIENT_ID", "")
UBBLE_CLIENT_SECRET = secrets_utils.get("UBBLE_CLIENT_SECRET", "")
UBBLE_WEBHOOK_SECRET = secrets_utils.get("UBBLE_WEBHOOK_SECRET")
UBBLE_SUBSCRIPTION_LIMITATION_DAYS = os.environ.get("UBBLE_SUBSCRIPTION_LIMITATION_DAYS", 90)

# Sandbox users and unit tests default password - overridden by a secret password on cloud environments
TEST_DEFAULT_PASSWORD = secrets_utils.get("TEST_DEFAULT_PASSWORD", "user@AZERTY123")

# Test users on staging
IMPORT_USERS_GOOGLE_DOCUMENT_ID = secrets_utils.get("IMPORT_USERS_GOOGLE_DOCUMENT_ID", "")


# PROVIDERS
ALLOCINE_API_KEY = secrets_utils.get("ALLOCINE_API_KEY")
CDS_API_URL = secrets_utils.get("CDS_API_URL")


# DEMARCHES SIMPLIFIEES
DMS_VENUE_PROCEDURE_ID = os.environ.get("DEMARCHES_SIMPLIFIEES_RIB_VENUE_PROCEDURE_ID")
DMS_VENUE_PROCEDURE_ID_V2 = os.environ.get("DEMARCHES_SIMPLIFIEES_RIB_VENUE_PROCEDURE_ID_V2")
DMS_VENUE_PROCEDURE_ID_V3 = os.environ.get("DEMARCHES_SIMPLIFIEES_RIB_VENUE_PROCEDURE_ID_V3")
DMS_VENUE_PROCEDURE_ID_V4 = os.environ.get("DEMARCHES_SIMPLIFIEES_RIB_VENUE_PROCEDURE_ID_V4")
DMS_TOKEN = secrets_utils.get("DEMARCHES_SIMPLIFIEES_TOKEN")
DMS_ENROLLMENT_INSTRUCTOR = os.environ.get("DEMARCHES_SIMPLIFIEES_ENROLLMENT_INSTRUCTOR", "")
DMS_NEW_ENROLLMENT_PROCEDURE_ID = int(os.environ.get("DEMARCHES_SIMPLIFIEES_ENROLLMENT_PROCEDURE_ID_v2", 0))
DMS_ENROLLMENT_PROCEDURE_ID_AFTER_GENERAL_OPENING = int(
    os.environ.get("DEMARCHES_SIMPLIFIEES_ENROLLMENT_PROCEDURE_ID_v3", 0)
)
DMS_ENROLLMENT_PROCEDURE_ID_v4_FR = int(os.environ.get("DEMARCHES_SIMPLIFIEES_ENROLLMENT_PROCEDURE_ID_v4_FR", 0))
DMS_ENROLLMENT_PROCEDURE_ID_v4_ET = int(os.environ.get("DEMARCHES_SIMPLIFIEES_ENROLLMENT_PROCEDURE_ID_v4_ET", 0))
DMS_WEBHOOK_TOKEN = secrets_utils.get("DEMARCHES_SIMPLIFIEES_WEBHOOK_TOKEN")
DMS_INACTIVITY_TOLERANCE_DELAY = int(os.environ.get("DEMARCHES_SIMPLIFIEES_INACTIVITY_TOLERANCE_DELAY", "90"))
DMS_INSTRUCTOR_ID = secrets_utils.get("DEMARCHES_SIMPLIFIEES_INSTRUCTOR_ID", "")

# OBJECT STORAGE
OBJECT_STORAGE_URL = secrets_utils.get("OBJECT_STORAGE_URL")
OBJECT_STORAGE_PROVIDER = os.environ.get("OBJECT_STORAGE_PROVIDER", _default_object_storage_provider)
LOCAL_STORAGE_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / "static" / "object_store_data"

# THUMBS
THUMBS_FOLDER_NAME = os.environ.get("THUMBS_FOLDER_NAME", "thumbs")

# GOOGLE
GCP_BUCKET_CREDENTIALS = json.loads(base64.b64decode(secrets_utils.get("GCP_BUCKET_CREDENTIALS", "")) or "{}")
GCP_BUCKET_NAME = os.environ.get("GCP_BUCKET_NAME", "")
GCP_ALTERNATE_BUCKET_NAME = os.environ.get("GCP_ALTERNATE_BUCKET_NAME", "")
GCP_DATA_BUCKET_NAME = secrets_utils.get("GCP_DATA_BUCKET_NAME", "")
GCP_DATA_PROJECT_ID = secrets_utils.get("GCP_DATA_PROJECT_ID", "")
GCP_CULTURAL_SURVEY_ANSWERS_QUEUE_NAME = os.environ.get("GCP_CULTURAL_SURVEY_ANSWERS_QUEUE_NAME", "")
GCP_ENCRYPTED_BUCKET_NAME = os.environ.get("GCP_ENCRYPTED_BUCKET_NAME", "")
GCP_PROJECT = os.environ.get("GCP_PROJECT", "")
GCP_REGION_CLOUD_TASK = os.environ.get("GCP_REGION_CLOUD_TASK", "europe-west3")
GCP_SENDINBLUE_CONTACTS_QUEUE_NAME = os.environ.get("GCP_SENDINBLUE_CONTACTS_QUEUE_NAME")
GCP_SENDINBLUE_PRO_QUEUE_NAME = os.environ.get("GCP_SENDINBLUE_PRO_QUEUE_NAME")
GCP_SENDINBLUE_TRANSACTIONAL_EMAILS_PRIMARY_QUEUE_NAME = os.environ.get(
    "GCP_SENDINBLUE_TRANSACTIONAL_EMAILS_PRIMARY_QUEUE_NAME"
)
GCP_SENDINBLUE_TRANSACTIONAL_EMAILS_SECONDARY_QUEUE_NAME = os.environ.get(
    "GCP_SENDINBLUE_TRANSACTIONAL_EMAILS_SECONDARY_QUEUE_NAME"
)
GCP_BATCH_CUSTOM_DATA_QUEUE_NAME = os.environ.get("GCP_BATCH_CUSTOM_DATA_QUEUE_NAME")
GCP_BATCH_CUSTOM_DATA_ANDROID_QUEUE_NAME = os.environ.get("GCP_BATCH_CUSTOM_DATA_ANDROID_QUEUE_NAME")
GCP_BATCH_CUSTOM_DATA_IOS_QUEUE_NAME = os.environ.get("GCP_BATCH_CUSTOM_DATA_IOS_QUEUE_NAME")
GCP_UBBLE_ARCHIVE_ID_PICTURES_QUEUE_NAME = os.environ.get("GCP_UBBLE_ARCHIVE_ID_PICTURES_QUEUE_NAME")
GCP_ZENDESK_ATTRIBUTES_QUEUE_NAME = os.environ.get("GCP_ZENDESK_ATTRIBUTES_QUEUE_NAME")

GCP_BATCH_NOTIFICATION_QUEUE_NAME = os.environ.get("GCP_BATCH_NOTIFICATION_QUEUE_NAME", "")

CLOUD_TASK_BEARER_TOKEN = secrets_utils.get("CLOUD_TASK_BEARER_TOKEN", "")
CLOUD_TASK_MAX_ATTEMPTS = int(os.environ.get("CLOUD_TASK_MAX_ATTEMPTS", 10))  # as 2022-8-8 in place for all cloud tasks

CLOUD_TASK_RETRY_INITIAL_DELAY = float(os.environ.get("CLOUD_TASK_RETRY_INITIAL_DELAY", 1.0))
CLOUD_TASK_RETRY_MAXIMUM_DELAY = float(os.environ.get("CLOUD_TASK_RETRY_MAXIMUM_DELAY", 60.0))
CLOUD_TASK_RETRY_MULTIPLIER = float(os.environ.get("CLOUD_TASK_RETRY_MULTIPLIER", 2.0))
CLOUD_TASK_RETRY_DEADLINE = float(os.environ.get("CLOUD_TASK_RETRY_DEADLINE", 60.0 * 2.0))

GOOGLE_CLIENT_ID = secrets_utils.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = secrets_utils.get("GOOGLE_CLIENT_SECRET")
GOOGLE_DRIVE_BACKEND = os.environ.get("GOOGLE_DRIVE_BACKEND", _default_google_drive_backend)


# RATE LIMITER
RATE_LIMIT_BY_EMAIL = os.environ.get("RATE_LIMIT_BY_EMAIL", "10/minute")
RATE_LIMIT_BY_IP = os.environ.get("RATE_LIMIT_BY_IP", "10/minute")
RATE_LIMIT_SIRENE_API = os.environ.get("RATE_LIMIT_SIRENE_API", "5/minute")


# DEBUG
DEBUG_ACTIVATED = os.environ.get("DEBUG_ACTIVATED") == "True"


# PHONE NUMBERS
BLACKLISTED_SMS_RECIPIENTS = set(secrets_utils.get("BLACKLISTED_SMS_RECIPIENTS", "").splitlines())

# USER PROFILING SERVICE
USER_PROFILING_URL = secrets_utils.get("USER_PROFILING_URL")
USER_PROFILING_ORG_ID = secrets_utils.get("USER_PROFILING_ORG_ID")
USER_PROFILING_API_KEY = secrets_utils.get("USER_PROFILING_API_KEY")

# APPSFLYER
APPS_FLYER_ANDROID_ID = os.environ.get("APPS_FLYER_ANDROID_ID", "app.passculture.webapp")
APPS_FLYER_IOS_ID = os.environ.get("APPS_FLYER_IOS_ID", "id1557887412")

APPS_FLYER_ANDROID_API_KEY = secrets_utils.get("APPS_FLYER_ANDROID_API_KEY", "")
APPS_FLYER_IOS_API_KEY = secrets_utils.get("APPS_FLYER_IOS_API_KEY", "")

# SEARCH
SEARCH_BACKEND = os.environ.get("SEARCH_BACKEND", _default_search_backend)

# ADAGE
ADAGE_API_KEY = secrets_utils.get("ADAGE_API_KEY", None)
ADAGE_API_URL = os.environ.get("ADAGE_API_URL", None)
EAC_API_KEY = secrets_utils.get("EAC_API_KEY", None)
JWT_ADAGE_PUBLIC_KEY_FILENAME = os.environ.get("JWT_ADAGE_PUBLIC_KEY_FILENAME", "public_key.production")
ADAGE_BACKEND = os.environ.get("ADAGE_BACKEND", "pcapi.core.educational.adage_backends.adage.AdageHttpClient")

# NOTION
NOTION_TOKEN = secrets_utils.get("NOTION_TOKEN", "")

# EDUCONNECT
API_URL_FOR_EDUCONNECT = os.environ.get(
    "API_URL_FOR_EDUCONNECT", API_URL
)  # must match the url specified in the metadata file provided to educonnect
EDUCONNECT_SP_CERTIFICATE = secrets_utils.get("EDUCONNECT_SP_CERTIFICATE", PUBLIC_CERTIFICATE_EXAMPLE)
EDUCONNECT_SP_PRIVATE_KEY = secrets_utils.get("EDUCONNECT_SP_PRIVATE_KEY", PRIVATE_KEY_EXAMPLE)

# PERMISSIONS
PERMISSIONS = base64.b64decode(secrets_utils.get("PERMISSIONS", "")).decode("utf-8")

# EMAIL UPDATES
MAX_EMAIL_UPDATE_ATTEMPTS = int(os.environ.get("MAX_EMAIL_UPDATE_ATTEMPTS", 2))
EMAIL_UPDATE_ATTEMPTS_TTL = int(os.environ.get("EMAIL_UPDATE_ATTEMPTS_TTL", 24 * 60 * 60 * 7))


# SOON EXPIRING BOOKINGS NOTIFICATIONS
SOON_EXPIRING_BOOKINGS_DAYS_BEFORE_EXPIRATION = int(os.environ.get("SOON_EXPIRING_BOOKINGS_DAYS_BEFORE_EXPIRATION", 3))


# SLACK
SLACK_BOT_TOKEN = secrets_utils.get("SLACK_BOT_TOKEN", None)
SLACK_CHANGE_FEATURE_FLIP_CHANNEL = os.environ.get("SLACK_CHANGE_FEATURE_FLIP_CHANNEL", "feature-flip-ehp")

# OUTSCALE
OUTSCALE_ACCESS_KEY = secrets_utils.get("OUTSCALE_ACCESS_KEY", "")
OUTSCALE_SECRET_KEY = secrets_utils.get("OUTSCALE_SECRET_KEY", "")
OUTSCALE_SECNUM_BUCKET_NAME = os.environ.get("OUTSCALE_SECNUM_BUCKET_NAME", "")
OUTSCALE_REGION = os.environ.get("OUTSCALE_REGION", "cloudgouv-eu-west-1")
OUTSCALE_ENDPOINT_URL = os.environ.get("OUTSCALE_ENDPOINT_URL", "https://oos.cloudgouv-eu-west-1.outscale.com")

# ZENDESK
ZENDESK_API_URL = os.environ.get("ZENDESK_API_URL")
ZENDESK_API_EMAIL = secrets_utils.get("ZENDESK_API_EMAIL")
ZENDESK_API_TOKEN = secrets_utils.get("ZENDESK_API_TOKEN")

# ACCOUNT (UN)SUSPENSION
DELETE_SUSPENDED_ACCOUNTS_SINCE = int(os.environ.get("DELETE_SUSPENDED_ACCOUNTS_SINCE", 61))

# FINANCE
FINANCE_GOOGLE_DRIVE_ROOT_FOLDER_ID = secrets_utils.get("FINANCE_GOOGLE_DRIVE_ROOT_FOLDER_ID", "")
FINANCE_OVERRIDE_PRICING_ORDERING_ON_SIRET_LIST = secrets_utils.get(
    "FINANCE_OVERRIDE_PRICING_ORDERING_ON_SIRET_LIST", ""
).split(",")

# BACKOFFICE
BACKOFFICE_USER_EMAIL = secrets_utils.get("BACKOFFICE_USER_EMAIL", "dummy.backoffice@example.com")
BACKOFFICE_SEARCH_SIMILARITY_MINIMAL_SCORE = float(os.environ.get("BACKOFFICE_SEARCH_SIMILARITY_MINIMAL_SCORE", 0.2))

# SIRENE
SIRENE_BACKEND = os.environ.get("SIRENE_BACKEND", _default_sirene_backend)
INSEE_SIRENE_API_TOKEN = secrets_utils.get("INSEE_SIRENE_API_TOKEN", "")
