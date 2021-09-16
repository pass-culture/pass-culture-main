from apscheduler.schedulers.blocking import BlockingScheduler
from sentry_sdk import set_tag

from pcapi import settings
from pcapi.core import search
from pcapi.core.logging import install_logging
import pcapi.core.offers.api as offers_api
from pcapi.scheduled_tasks import utils
from pcapi.scheduled_tasks.decorators import cron_context
from pcapi.scheduled_tasks.decorators import log_cron


install_logging()


# FIXME (dbaty, 2021-06-16): rename the file and the cron (and the
# name of the pod).
@log_cron
@cron_context
def index_offers_in_algolia_by_offer(app):
    search.index_offers_in_queue()


@log_cron
@cron_context
def index_offers_in_algolia_by_venue(app):
    search.index_offers_of_venues_in_queue()


@log_cron
@cron_context
def delete_expired_offers_in_algolia(app):
    offers_api.unindex_expired_offers()


@log_cron
@cron_context
def index_offers_in_error_in_algolia_by_offer(app):
    search.index_offers_in_queue(from_error_queue=True)


def main():
    from pcapi.flask_app import app

    set_tag("pcapi.app_type", "algolia_clock")
    scheduler = BlockingScheduler()

    utils.activate_sentry(scheduler)

    scheduler.add_job(
        index_offers_in_algolia_by_offer,
        "cron",
        [app],
        minute=settings.ALGOLIA_CRON_INDEXING_OFFERS_BY_OFFER_FREQUENCY,
        max_instances=4,
    )

    scheduler.add_job(
        index_offers_in_algolia_by_venue,
        "cron",
        [app],
        minute=settings.ALGOLIA_CRON_INDEXING_OFFERS_BY_VENUE_PROVIDER_FREQUENCY,
    )

    scheduler.add_job(delete_expired_offers_in_algolia, "cron", [app], day="*", hour="1")

    scheduler.add_job(
        index_offers_in_error_in_algolia_by_offer,
        "cron",
        [app],
        minute=settings.ALGOLIA_CRON_INDEXING_OFFERS_IN_ERROR_BY_OFFER_FREQUENCY,
    )

    scheduler.start()


if __name__ == "__main__":
    main()
