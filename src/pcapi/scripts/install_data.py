import logging

from flask import current_app as app

from pcapi.install_database_extensions import install_database_extensions


logger = logging.getLogger(__name__)


# FIXME (apibrac, 2021-04-08): this command is used during deploy process
# Remove it when the post deploy command is brought back in this repo
# and it is modified wihtout install_data, but not before
@app.manager.command
def install_data():
    logger.info("install_data: Nothing to do here")


@app.manager.command
def install_postgres_extension():
    install_database_extensions(app)
    logger.info("Database extensions installed")
