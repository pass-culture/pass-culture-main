import logging

from flask import Flask

from pcapi.flask_integration.app_builder.backend import BackendAppBuilder
from pcapi.flask_integration.utils import build_app


logger = logging.getLogger(__name__)


def create_app() -> Flask:
    # needs a backend app for generate_public_api_openapi_json script
    return build_app(BackendAppBuilder())


app = create_app()
