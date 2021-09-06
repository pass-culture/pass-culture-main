import logging

from flask import current_app as app

from pcapi.install_database_extensions import install_database_extensions
from pcapi.scripts.install_database_feature_flags import install_database_feature_flags


logger = logging.getLogger(__name__)


@app.manager.command
def install_data():
    install_database_feature_flags(app)
    logger.info("Feature flags installed")


@app.manager.command
def install_postgres_extension():
    install_database_extensions(app)
    logger.info("Database extensions installed")
