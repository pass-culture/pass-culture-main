from apscheduler.schedulers.blocking import BlockingScheduler
from flask import Blueprint
from sentry_sdk import set_tag

from pcapi.local_providers.provider_manager import synchronize_data_for_provider
from pcapi.models.feature import FeatureToggle
from pcapi.scheduled_tasks import utils
from pcapi.scheduled_tasks.decorators import cron_context
from pcapi.scheduled_tasks.decorators import cron_require_feature
from pcapi.scheduled_tasks.decorators import log_cron_with_transaction


blueprint = Blueprint(__name__, __name__)


@cron_context
@log_cron_with_transaction
@cron_require_feature(FeatureToggle.SYNCHRONIZE_TITELIVE_PRODUCTS)
def synchronize_titelive_things(app):
    synchronize_data_for_provider("TiteLiveThings")


@cron_context
@log_cron_with_transaction
@cron_require_feature(FeatureToggle.SYNCHRONIZE_TITELIVE_PRODUCTS_DESCRIPTION)
def synchronize_titelive_thing_descriptions(app):
    synchronize_data_for_provider("TiteLiveThingDescriptions")


@cron_context
@log_cron_with_transaction
@cron_require_feature(FeatureToggle.SYNCHRONIZE_TITELIVE_PRODUCTS_THUMBS)
def synchronize_titelive_thing_thumbs(app):
    synchronize_data_for_provider("TiteLiveThingThumbs")


@blueprint.cli.command("titelive_clock")
def titelive_clock():
    from flask import current_app as app

    set_tag("pcapi.app_type", "titelive_clock")
    scheduler = BlockingScheduler()
    utils.activate_sentry(scheduler)

    scheduler.add_job(synchronize_titelive_things, "cron", [app], day="*", hour="1")

    scheduler.add_job(synchronize_titelive_thing_descriptions, "cron", [app], day="*", hour="2")

    scheduler.add_job(synchronize_titelive_thing_thumbs, "cron", [app], day="*", hour="3")

    scheduler.start()
