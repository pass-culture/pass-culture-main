import logging

from pcapi.core.permissions import models as perm_models
from pcapi.install_database_extensions import install_database_extensions
from pcapi.models import db
from pcapi.models.feature import install_feature_flags
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)


@blueprint.cli.command("install_data")
def install_data() -> None:
    install_feature_flags()
    logger.info("Feature flags installed")

    perm_models.sync_db_permissions(db.session)
    logger.info("Permissions synced")

    perm_models.sync_db_roles(db.session)
    logger.info("Roles synced")


@blueprint.cli.command("install_postgres_extensions")
def install_postgres_extensions() -> None:
    install_database_extensions()
    logger.info("Database extensions installed")
