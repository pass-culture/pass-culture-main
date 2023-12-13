from pcapi.core.offerers.update_offerer_stats import delete_offerer_old_stats
from pcapi.core.offerers.update_offerer_stats import update_offerer_daily_views_stats
from pcapi.core.offerers.update_offerer_stats import update_offerer_top_views_stats
from pcapi.models.feature import FeatureToggle
from pcapi.scheduled_tasks.decorators import cron_require_feature
from pcapi.scheduled_tasks.decorators import log_cron_with_transaction
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)


@blueprint.cli.command("update_offerer_stats")
@log_cron_with_transaction
@cron_require_feature(FeatureToggle.ENABLE_CRON_TO_UPDATE_OFFERER_STATS)
def update_offerer_stats() -> None:
    """Updated the offrer stats in the database from big query"""
    update_offerer_daily_views_stats()
    update_offerer_top_views_stats()
    delete_offerer_old_stats()
