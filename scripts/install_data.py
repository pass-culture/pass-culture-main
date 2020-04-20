from flask import current_app as app

from local_providers.install import install_local_providers
from models.install import install_models, install_database_extensions
from utils.logger import logger

@app.manager.command
def install_data():
    with app.app_context():
        install_models()
        install_local_providers()
    logger.info("Models and LocalProviders installed")


@app.manager.command
def install_postgres_extension():
    with app.app_context():
        install_database_extensions()
    logger.info("Database extensions installed")
