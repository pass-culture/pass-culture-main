from apscheduler.schedulers.blocking import BlockingScheduler
from sentry_sdk import set_tag

from pcapi import settings
from pcapi.core import search
import pcapi.core.offers.api as offers_api
from pcapi.scheduled_tasks import utils
from pcapi.scheduled_tasks.decorators import cron_context
from pcapi.scheduled_tasks.decorators import log_cron_with_transaction
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)


# FIXME (dbaty, 2021-06-16): rename the file and the cron (and the
# name of the pod).
@cron_context
@log_cron_with_transaction
def index_offers_in_algolia_by_offer():
    search.index_offers_in_queue()


@cron_context
@log_cron_with_transaction
def index_offers_in_algolia_by_venue():
    search.index_offers_of_venues_in_queue()


@cron_context
@log_cron_with_transaction
def delete_expired_offers_in_algolia():
    offers_api.unindex_expired_offers()


@cron_context
@log_cron_with_transaction
def index_offers_in_error_in_algolia_by_offer():
    search.index_offers_in_queue(from_error_queue=True)


@cron_context
@log_cron_with_transaction
def index_venues():
    search.index_venues_in_queue()


@cron_context
@log_cron_with_transaction
def index_venues_in_error():
    search.index_venues_in_queue(from_error_queue=True)


@blueprint.cli.command("algolia_clock")
def algolia_clock():
    set_tag("pcapi.app_type", "algolia_clock")
    scheduler = BlockingScheduler()
    utils.activate_sentry(scheduler)

    # ---- Offers ----- #

    scheduler.add_job(
        index_offers_in_algolia_by_offer,
        "cron",
        minute=settings.ALGOLIA_CRON_INDEXING_OFFERS_BY_OFFER_FREQUENCY,
        max_instances=4,
    )

    scheduler.add_job(
        index_offers_in_algolia_by_venue,
        "cron",
        minute=settings.ALGOLIA_CRON_INDEXING_OFFERS_BY_VENUE_PROVIDER_FREQUENCY,
    )

    scheduler.add_job(delete_expired_offers_in_algolia, "cron", day="*", hour="1")

    scheduler.add_job(
        index_offers_in_error_in_algolia_by_offer,
        "cron",
        minute=settings.ALGOLIA_CRON_INDEXING_OFFERS_IN_ERROR_BY_OFFER_FREQUENCY,
    )

    # ---- Venues ----- #

    scheduler.add_job(
        index_venues,
        "cron",
        minute=settings.CRON_INDEXING_VENUES_FREQUENCY,
    )

    scheduler.add_job(
        index_venues_in_error,
        "cron",
        minute=settings.CRON_INDEXING_VENUES_IN_ERROR_FREQUENCY,
    )

    scheduler.start()
