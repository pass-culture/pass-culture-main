from pcapi.local_providers.provider_manager import synchronize_data_for_provider
from pcapi.models.feature import FeatureToggle
from pcapi.scheduled_tasks.decorators import cron_require_feature
from pcapi.scheduled_tasks.decorators import log_cron_with_transaction
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)


@blueprint.cli.command("synchronize_titelive_things")
@log_cron_with_transaction
@cron_require_feature(FeatureToggle.SYNCHRONIZE_TITELIVE_PRODUCTS)
def synchronize_titelive_things():
    """Launches Titelive products synchronization through TiteLiveThings provider"""
    synchronize_data_for_provider("TiteLiveThings")


@blueprint.cli.command("synchronize_titelive_thing_descriptions")
@log_cron_with_transaction
@cron_require_feature(FeatureToggle.SYNCHRONIZE_TITELIVE_PRODUCTS_DESCRIPTION)
def synchronize_titelive_thing_descriptions():
    """Launches Titelive descriptions synchronization through TiteLiveThingDescriptions provider"""
    synchronize_data_for_provider("TiteLiveThingDescriptions")


@blueprint.cli.command("synchronize_titelive_thing_thumbs")
@log_cron_with_transaction
@cron_require_feature(FeatureToggle.SYNCHRONIZE_TITELIVE_PRODUCTS_THUMBS)
def synchronize_titelive_thing_thumbs():
    """Launches Titelive thumbs synchronization through TiteLiveThingThumbs provider"""
    synchronize_data_for_provider("TiteLiveThingThumbs")
