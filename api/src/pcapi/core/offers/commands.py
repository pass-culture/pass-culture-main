import click

import pcapi.core.offers.api as offers_api
from pcapi.scheduled_tasks.decorators import log_cron_with_transaction
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)


@blueprint.cli.command("activate_future_offers")
@log_cron_with_transaction
def activate_future_offers() -> None:
    offers_api.activate_future_offers_and_remind_users()


@blueprint.cli.command("set_upper_timespan_of_inactive_headline_offers")
@log_cron_with_transaction
def set_upper_timespan_of_inactive_headline_offers() -> None:
    offers_api.set_upper_timespan_of_inactive_headline_offers()


@blueprint.cli.command("delete_unbookable_unbooked_old_offers")
@click.argument("min_offer_id", required=False, type=int, default=0)
@click.argument("max_offer_id", required=False, type=int, default=None)
@click.argument("offer_chunk_size", required=False, type=int, default=16)
@log_cron_with_transaction
def delete_unbookable_unbooked_old_offers(min_offer_id: int, max_offer_id: int | None, offer_chunk_size: int) -> None:
    offers_api.delete_unbookable_unbooked_old_offers(min_offer_id, max_offer_id, offer_chunk_size)
