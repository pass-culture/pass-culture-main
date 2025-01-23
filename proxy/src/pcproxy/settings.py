import os


ENV = os.environ.get("ENV", "development")

JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")

# Recommendation API
RECOMMENDATION_API_AUTHENTICATION_TOKEN = os.environ.get("RECOMMENDATION_API_AUTHENTICATION_TOKEN")
RECOMMENDATION_API_URL = os.environ.get("RECOMMENDATION_API_URL", "http://127.0.0.1:8000")
# SENTRY
ENABLE_SENTRY = bool(int(os.environ.get("ENABLE_SENTRY", 0)))
SENTRY_DSN = os.environ.get("SENTRY_DSN", "")
SENTRY_DEFAULT_TRACES_SAMPLE_RATE = float(os.environ.get("SENTRY_DEFAULT_TRACES_SAMPLE_RATE", 0))
