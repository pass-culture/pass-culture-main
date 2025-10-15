import logging

import click

import pcapi.utils.cron as cron_decorators
from pcapi.core.permissions import models as perm_models
from pcapi.db_utils import install_database_extensions
from pcapi.models import db
from pcapi.models import feature as feature_models
from pcapi.models.feature import check_feature_flags_completeness
from pcapi.models.feature import clean_feature_flags
from pcapi.models.feature import install_feature_flags
from pcapi.utils import requests
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


@blueprint.cli.command("clean_data")
def clean_data() -> None:
    clean_feature_flags()
    logger.info("Feature flags cleaned")


@blueprint.cli.command("check_feature_flags")
@cron_decorators.log_cron_with_transaction
def check_feature_flags() -> None:
    check_feature_flags_completeness()


@blueprint.cli.command("install_postgres_extensions")
def install_postgres_extensions() -> None:
    install_database_extensions()
    logger.info("Database extensions installed")


TARGET_URL_MAP = {
    "testing": "https://backend.testing.passculture.team/features",
    "staging": "https://backend.staging.passculture.team/features",
    "production": "https://backend.passculture.app/features",
    "integration": "https://backend.integration.passculture.team/features",
}


def get_ff_from_target(target: str) -> dict[str, bool]:
    response = requests.get(TARGET_URL_MAP[target])
    assert response.status_code == 200, f"Failed to fetch feature flags from production: {response.status_code}"
    return {ff["name"]: ff["isActive"] for ff in response.json()}


@blueprint.cli.command("check_feature_flags_vs")
@click.option(
    "--target",
    type=click.Choice(["testing", "staging", "production", "integration"], case_sensitive=False),
    help="Compares local feature flags vs remonte platform.",
    required=True,
)
@cron_decorators.log_cron_with_transaction
def check_feature_flags_vs(target: str) -> None:
    remote_flags = get_ff_from_target(target)
    local_flags = {ff.name: ff.isActive for ff in db.session.query(feature_models.Feature).all()}
    for flag_name in remote_flags.keys():
        if flag_name not in local_flags:
            logger.warning(f"Feature flag {flag_name} exists in {target} but not locally")
        if remote_flags[flag_name] != local_flags[flag_name]:
            logger.warning(
                f"Feature flag {flag_name} has different values: {target}={remote_flags[flag_name]}, local={local_flags[flag_name]}"
            )
