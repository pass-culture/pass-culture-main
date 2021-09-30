import logging

from flask import Blueprint

from pcapi.install_database_extensions import install_database_extensions
from pcapi.scripts.install_database_feature_flags import install_database_feature_flags


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)


@blueprint.cli.command("install_data")
def install_data():
    from flask import current_app

    install_database_feature_flags(current_app)
    logger.info("Feature flags installed")


@blueprint.cli.command("install_postgres_extension")
def install_postgres_extension():
    from flask import current_app

    install_database_extensions(current_app)
    logger.info("Database extensions installed")
