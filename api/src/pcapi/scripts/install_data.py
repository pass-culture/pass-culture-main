import logging

from pcapi.db_utils import install_database_extensions
from pcapi.db_utils import sync_enums_with_db
from pcapi.models import feature as feature_models
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)


@blueprint.cli.command("install_data")
def install_data() -> None:
    sync_enums_with_db()


@blueprint.cli.command("clean_data")
def clean_data() -> None:
    feature_models.clean_feature_flags()

    logger.info("Feature flags cleaned")


@blueprint.cli.command("install_postgres_extensions")
def install_postgres_extensions() -> None:
    install_database_extensions()
    logger.info("Database extensions installed")
