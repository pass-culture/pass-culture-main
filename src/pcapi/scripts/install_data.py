from flask import current_app as app

from pcapi.install_database_extensions import install_database_extensions
from pcapi.local_providers.install import install_local_providers
from pcapi.models.install import install_activity
from pcapi.utils.logger import logger

@app.manager.command
def install_data():
    with app.app_context():
        install_activity()
        install_local_providers()
    logger.info("Models and LocalProviders installed")


@app.manager.command
def install_postgres_extension():
    install_database_extensions(app)
    logger.info("Database extensions installed")
