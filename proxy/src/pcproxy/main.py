from fastapi import FastAPI
import sentry_sdk

from pcproxy import settings
from pcproxy.utils.routes import install_routes


app = FastAPI()

if settings.ENABLE_SENTRY:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENV,
        traces_sample_rate=settings.SENTRY_DEFAULT_TRACES_SAMPLE_RATE / 1000,
        max_value_length=8192,
    )

install_routes()
