import datetime
import decimal
import logging

import click
import sqlalchemy.orm as sqla_orm

from pcapi import settings
from pcapi.core.finance import ds
import pcapi.core.finance.api as finance_api
import pcapi.core.finance.exceptions as finance_exceptions
import pcapi.core.finance.models as finance_models
import pcapi.core.finance.utils as finance_utils
import pcapi.core.offers.models as offers_models
from pcapi.models.feature import FeatureToggle
from pcapi.notifications.internal import send_internal_message
import pcapi.scheduled_tasks.decorators as cron_decorators
from pcapi.utils.blueprint import Blueprint
import pcapi.utils.date as date_utils


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)


@blueprint.cli.command("price_finance_events")
@cron_decorators.log_cron_with_transaction
@cron_decorators.cron_require_feature(FeatureToggle.PRICE_FINANCE_EVENTS)
def price_finance_events() -> None:
    """Price finance events that have recently been created."""
    finance_api.price_events()


@blueprint.cli.command("generate_cashflows_and_payment_files")
@click.option("--override-feature-flag", help="Override feature flag", is_flag=True, default=False)
@click.option("--cutoff", help="Datetime cutoff to put in UTC timezone", type=datetime.datetime, required=False)
@cron_decorators.log_cron_with_transaction
def generate_cashflows_and_payment_files(override_feature_flag: bool, cutoff: datetime.datetime) -> None:
    flag = FeatureToggle.GENERATE_CASHFLOWS_BY_CRON
    if not override_feature_flag and not flag.is_active():
        logger.info("%s is not active, cronjob will not run.", flag.name)
        return
    if not cutoff:
        last_day = datetime.date.today() - datetime.timedelta(days=1)
        cutoff = finance_utils.get_cutoff_as_datetime(last_day)

    finance_api.generate_cashflows_and_payment_files(cutoff)


@blueprint.cli.command("generate_invoices")
@click.option("--batch-id", type=int, required=True)
def generate_invoices(batch_id: int) -> None:
    """Generate (and store) all invoices of a CashflowBatch.

    This command can be run multiple times.
    """
    batch = finance_models.CashflowBatch.query.get(batch_id)
    if not batch:
        print(f"Could not generate invoices for this batch, as it doesn't exist :{batch_id}")
        return

    try:
        finance_api.generate_invoices(batch)
    except finance_exceptions.NoInvoiceToGenerate:
        logger.info("No invoice to generate")
    finally:
        finance_api.generate_debit_notes(batch)

    if settings.SLACK_GENERATE_INVOICES_FINISHED_CHANNEL:
        send_internal_message(
            channel=settings.SLACK_GENERATE_INVOICES_FINISHED_CHANNEL,
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"La Génération de factures ({batch.label}) est terminée avec succès",
                    },
                }
            ],
            icon_emoji=":large_green_circle:",
        )


@blueprint.cli.command("add_custom_offer_reimbursement_rule")
@click.option("--offer-id", required=True)
@click.option("--offer-original-amount", required=True)
@click.option("--offerer-id", type=int, required=True)
@click.option("--reimbursed-amount", required=True)
@click.option("--valid-from", required=True)
@click.option("--valid-until", required=False)
@click.option("--force", required=False, is_flag=True, help="Ignore warnings and create rule anyway")
def add_custom_offer_reimbursement_rule(
    offer_id: str,
    offer_original_amount: str,
    offerer_id: int,
    reimbursed_amount: str,
    valid_from: str,
    valid_until: str | None = None,
    force: bool = False,
) -> None:
    """Add a custom reimbursement rule that is linked to an offer."""
    offer_original_amount = decimal.Decimal(offer_original_amount.replace(",", "."))  # type: ignore[assignment]
    reimbursed_amount = decimal.Decimal(reimbursed_amount.replace(",", "."))  # type: ignore[assignment]

    offer = (
        offers_models.Offer.query.options(
            sqla_orm.joinedload(offers_models.Offer.stocks, innerjoin=True),
            sqla_orm.joinedload(offers_models.Offer.venue, innerjoin=True),
        )
        .filter_by(id=offer_id)
        .one_or_none()
    )
    if not offer:
        print(f"Could not find offer: {offer_id}")
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
        amount=reimbursed_amount,  # type: ignore[arg-type]
        start_date=valid_from_dt,
        end_date=valid_until_dt,
    )
    print(f"Created new rule: {rule.id}")


@blueprint.cli.command("recredit_underage_users")
@cron_decorators.log_cron_with_transaction
def recredit_underage_users() -> None:
    finance_api.recredit_underage_users()


@blueprint.cli.command("import_ds_bank_information_applications")
@cron_decorators.log_cron_with_transaction
def import_ds_bank_information_applications() -> None:
    procedures = [
        settings.DS_BANK_ACCOUNT_PROCEDURE_ID,
        settings.DMS_VENUE_PROCEDURE_ID_V4,
    ]
    for procedure in procedures:
        if not procedure:
            logger.info("Skipping DS %s because procedure id is empty", procedure)
            continue
        ds.import_ds_bank_information_applications(procedure_number=int(procedure))
