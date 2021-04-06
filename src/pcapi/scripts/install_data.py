import logging

from flask import current_app as app

from pcapi.install_database_extensions import install_database_extensions
from pcapi.models.install import install_activity


logger = logging.getLogger(__name__)


@app.manager.command
def install_data():
    with app.app_context():
        install_activity()
    logger.info("Models installed")


@app.manager.command
def install_postgres_extension():
    install_database_extensions(app)
    logger.info("Database extensions installed")
