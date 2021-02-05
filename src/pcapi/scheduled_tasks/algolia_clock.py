from apscheduler.schedulers.blocking import BlockingScheduler

from pcapi import settings
from pcapi.algolia.infrastructure.worker import process_multi_indexing
from pcapi.models.feature import FeatureToggle
from pcapi.scheduled_tasks import utils
from pcapi.scheduled_tasks.decorators import cron_context
from pcapi.scheduled_tasks.decorators import cron_require_feature
from pcapi.scheduled_tasks.decorators import log_cron
from pcapi.scripts.algolia_indexing.indexing import batch_deleting_expired_offers_in_algolia
from pcapi.scripts.algolia_indexing.indexing import batch_indexing_offers_in_algolia_by_offer
from pcapi.scripts.algolia_indexing.indexing import batch_indexing_offers_in_algolia_by_venue
from pcapi.scripts.algolia_indexing.indexing import batch_processing_offer_ids_in_error


@log_cron
@cron_context
@cron_require_feature(FeatureToggle.SYNCHRONIZE_ALGOLIA)
def index_offers_in_algolia_by_offer(app):
    batch_indexing_offers_in_algolia_by_offer(client=app.redis_client)


@log_cron
@cron_context
@cron_require_feature(FeatureToggle.SYNCHRONIZE_ALGOLIA)
def index_offers_in_algolia_by_venue(app):
    batch_indexing_offers_in_algolia_by_venue(client=app.redis_client)


@log_cron
@cron_context
@cron_require_feature(FeatureToggle.SYNCHRONIZE_ALGOLIA)
@cron_require_feature(FeatureToggle.ENABLE_WHOLE_VENUE_PROVIDER_ALGOLIA_INDEXATION)
def index_offers_in_algolia_by_venue_provider(app):
    process_multi_indexing(client=app.redis_client)


@log_cron
@cron_context
@cron_require_feature(FeatureToggle.SYNCHRONIZE_ALGOLIA)
def delete_expired_offers_in_algolia(app):
    batch_deleting_expired_offers_in_algolia(client=app.redis_client)


@log_cron
@cron_context
@cron_require_feature(FeatureToggle.SYNCHRONIZE_ALGOLIA)
def index_offers_in_error_in_algolia_by_offer(app):
    batch_processing_offer_ids_in_error(client=app.redis_client)


def main():
    from pcapi.flask_app import app

    scheduler = BlockingScheduler()
    utils.activate_sentry(scheduler)

    scheduler.add_job(
        index_offers_in_algolia_by_offer, "cron", [app], minute=settings.ALGOLIA_CRON_INDEXING_OFFERS_BY_OFFER_FREQUENCY
    )

    scheduler.add_job(
        index_offers_in_algolia_by_venue_provider,
        "cron",
        [app],
        minute=settings.ALGOLIA_CRON_INDEXING_OFFERS_BY_VENUE_FREQUENCY,
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
