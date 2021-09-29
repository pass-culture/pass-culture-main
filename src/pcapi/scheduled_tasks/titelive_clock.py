"""
    isort:skip_file
"""
from apscheduler.schedulers.blocking import BlockingScheduler
from sentry_sdk import set_tag

# FIXME (asaunier, 2021-04-20): this is to prevent circular imports
import pcapi.models  # pylint: disable=unused-import
from pcapi.core.logging import install_logging
from pcapi.local_providers.provider_manager import synchronize_data_for_provider
from pcapi.models.feature import FeatureToggle
from pcapi.scheduled_tasks import utils
from pcapi.scheduled_tasks.decorators import cron_context
from pcapi.scheduled_tasks.decorators import cron_require_feature
from pcapi.scheduled_tasks.decorators import log_cron_with_transaction


install_logging()


@log_cron_with_transaction
@cron_context
@cron_require_feature(FeatureToggle.SYNCHRONIZE_TITELIVE_PRODUCTS)
def synchronize_titelive_things(app):
    synchronize_data_for_provider("TiteLiveThings")


@log_cron_with_transaction
@cron_context
@cron_require_feature(FeatureToggle.SYNCHRONIZE_TITELIVE_PRODUCTS_DESCRIPTION)
def synchronize_titelive_thing_descriptions(app):
    synchronize_data_for_provider("TiteLiveThingDescriptions")


@log_cron_with_transaction
@cron_context
@cron_require_feature(FeatureToggle.SYNCHRONIZE_TITELIVE_PRODUCTS_THUMBS)
def synchronize_titelive_thing_thumbs(app):
    synchronize_data_for_provider("TiteLiveThingThumbs")


def main():
    from pcapi.flask_app import app

    set_tag("pcapi.app_type", "titelive_clock")
    scheduler = BlockingScheduler()
    utils.activate_sentry(scheduler)

    scheduler.add_job(synchronize_titelive_things, "cron", [app], day="*", hour="1")

    scheduler.add_job(synchronize_titelive_thing_descriptions, "cron", [app], day="*", hour="2")

    scheduler.add_job(synchronize_titelive_thing_thumbs, "cron", [app], day="*", hour="3")

    scheduler.start()


if __name__ == "__main__":
    main()
