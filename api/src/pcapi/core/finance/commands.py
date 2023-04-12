import datetime
import decimal
import logging

import click
import sqlalchemy.orm as sqla_orm

from pcapi.core.finance import siret_api
import pcapi.core.finance.api as finance_api
import pcapi.core.finance.utils as finance_utils
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.models as offers_models
from pcapi.models.feature import FeatureToggle
import pcapi.scheduled_tasks.decorators as cron_decorators
from pcapi.utils import human_ids
from pcapi.utils.blueprint import Blueprint
import pcapi.utils.date as date_utils


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)


@blueprint.cli.command("price_bookings")
@cron_decorators.log_cron_with_transaction
@cron_decorators.cron_require_feature(FeatureToggle.PRICE_BOOKINGS)
def price_bookings() -> None:
    """Price bookings that have been recently marked as used."""
    finance_api.price_bookings()


@blueprint.cli.command("price_finance_events")
@cron_decorators.log_cron_with_transaction
@cron_decorators.cron_require_feature(FeatureToggle.PRICE_FINANCE_EVENTS)
def price_finance_events() -> None:
    """Price finance events that have recently been created."""
    finance_api.price_events()


@blueprint.cli.command("generate_cashflows_and_payment_files")
@click.option("--override-feature-flag", help="Override feature flag", is_flag=True, default=False)
@cron_decorators.log_cron_with_transaction
def generate_cashflows_and_payment_files(override_feature_flag: bool) -> None:
    flag = FeatureToggle.GENERATE_CASHFLOWS_BY_CRON
    if not override_feature_flag and not flag.is_active():
        logger.info("%s is not active, cronjob will not run.", flag.name)
        return
    last_day = datetime.date.today() - datetime.timedelta(days=1)
    cutoff = finance_utils.get_cutoff_as_datetime(last_day)
    finance_api.generate_cashflows_and_payment_files(cutoff)


@blueprint.cli.command("generate_invoices")
def generate_invoices() -> None:
    """Generate (and store) all invoices.

    This command can be run multiple times.
    """
    finance_api.generate_invoices()


@blueprint.cli.command("add_custom_offer_reimbursement_rule")  # type: ignore [arg-type]
@click.option("--offer-humanized-id", required=True)
@click.option("--offer-original-amount", required=True)
@click.option("--offerer-id", type=int, required=True)
@click.option("--reimbursed-amount", required=True)
@click.option("--valid-from", required=True)
@click.option("--valid-until", required=False)
@click.option("--force", required=False, is_flag=True, help="Ignore warnings and create rule anyway")
def add_custom_offer_reimbursement_rule(
    offer_humanized_id: str,
    offer_original_amount: str,
    offerer_id: int,
    reimbursed_amount: str,
    valid_from: str,
    valid_until: str = None,
    force: bool = False,
) -> None:
    """Add a custom reimbursement rule that is linked to an offer."""
    offer_original_amount = decimal.Decimal(offer_original_amount.replace(",", "."))  # type: ignore [assignment]
    reimbursed_amount = decimal.Decimal(reimbursed_amount.replace(",", "."))  # type: ignore [assignment]

    offer_id = human_ids.dehumanize(offer_humanized_id)
    offer = (
        offers_models.Offer.query.options(
            sqla_orm.joinedload(offers_models.Offer.stocks, innerjoin=True),
            sqla_orm.joinedload(offers_models.Offer.venue, innerjoin=True),
        )
        .filter_by(id=offer_id)
        .one_or_none()
    )
    if not offer:
        print(f"Could not find offer: {offer_humanized_id}")
        return

    warnings = []
    if offer.venue.managingOffererId != offerer_id:
        warnings.append(f"Mismatch on offerer: given {offerer_id}, expected {offer.venue.managingOffererId}")

    stock_amounts = {stock.price for stock in offer.stocks}
    if len(stock_amounts) > 1:
        warnings.append(f"Possible mismatch on original amount: found multiple amounts in database: {stock_amounts}")
    stock_amount = stock_amounts.pop()
    if offer_original_amount != stock_amount:
        warnings.append(f"Mismatch on original amount: given {offer_original_amount}, expected {stock_amount}")

    if warnings:
        print("Found multiple warnings. Double-check that the command has been given the right information.")
        print("\n".join(warnings))
        if not force:
            print(
                "Command has failed. Use `--force` if you are really sure that you "
                "want to ignore warnings and proceed anyway."
            )
            return

    valid_from_dt = date_utils.get_day_start(
        datetime.date.fromisoformat(valid_from),
        finance_utils.ACCOUNTING_TIMEZONE,
    )
    valid_until_dt = (
        date_utils.get_day_start(
            datetime.date.fromisoformat(valid_until),
            finance_utils.ACCOUNTING_TIMEZONE,
        )
        if valid_until
        else None
    )

    rule = finance_api.create_offer_reimbursement_rule(
        offer_id=offer.id,
        amount=reimbursed_amount,  # type: ignore [arg-type]
        start_date=valid_from_dt,
        end_date=valid_until_dt,
    )
    print(f"Created new rule: {rule.id}")


@blueprint.cli.command("move_siret")  # type: ignore [arg-type]
@click.option("--src-venue-id", type=int, required=True)
@click.option("--dst-venue-id", type=int, required=True)
@click.option("--siret", required=True)
@click.option("--comment", required=True)
@click.option("--apply-changes", is_flag=True, default=False, required=False)
@click.option("--override-revenue-check", is_flag=True, default=False, required=False)
def move_siret(
    src_venue_id: int,
    dst_venue_id: int,
    siret: str,
    comment: str,
    apply_changes: bool = False,
    override_revenue_check: bool = False,
) -> None:
    source = offerers_models.Venue.query.get(src_venue_id)
    target = offerers_models.Venue.query.get(dst_venue_id)

    try:
        siret_api.move_siret(
            source,
            target,
            siret,
            comment,
            apply_changes=apply_changes,
            override_revenue_check=override_revenue_check,
        )
    except siret_api.CheckError as exc:
        print(str(exc))
        return

    if apply_changes:
        print("Siret has been moved.")
    else:
        print("DRY RUN: NO CHANGES HAVE BEEN MADE")


@blueprint.cli.command("recredit_underage_users")
@cron_decorators.log_cron_with_transaction
def recredit_underage_users() -> None:
    finance_api.recredit_underage_users()
