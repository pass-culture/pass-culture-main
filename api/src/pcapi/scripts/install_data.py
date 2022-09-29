import logging

from pcapi.install_database_extensions import install_database_extensions
from pcapi.models.feature import install_feature_flags
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)


@blueprint.cli.command("install_data")
def install_data() -> None:
    install_feature_flags()
    logger.info("Feature flags installed")
    logger.info("Permissions synced")


@blueprint.cli.command("install_postgres_extensions")
def install_postgres_extensions() -> None:
    install_database_extensions()
    logger.info("Database extensions installed")
