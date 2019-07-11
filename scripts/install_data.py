from local_providers.install import install_local_providers
from models.install import install_models
from flask import current_app as app

from models.mediation import upsert_tuto_mediations
from utils.logger import logger


@app.manager.command
def install_data():
    with app.app_context():
        install_models()
        upsert_tuto_mediations()
        install_local_providers()
    logger.info("Models and LocalProviders installed")
