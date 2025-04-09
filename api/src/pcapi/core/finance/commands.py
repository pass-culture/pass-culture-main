import datetime
import decimal
import logging

import click
import sqlalchemy.orm as sa_orm

from pcapi import settings
from pcapi.connectors.dms.utils import import_ds_applications
from pcapi.core.finance import ds
from pcapi.core.finance import external as finance_external
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
from pcapi.workers.export_csv_and_send_notification_emails_job import export_csv_and_send_notification_emails_job


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
@click.option("--with-invoices", help="Launch invoices generation after cashflows generation", type=bool, default=True)
@cron_decorators.log_cron_with_transaction
def generate_cashflows_and_payment_files(
    override_feature_flag: bool, cutoff: datetime.datetime, with_invoices: bool
) -> None:
    flag = FeatureToggle.GENERATE_CASHFLOWS_BY_CRON
    if not override_feature_flag and not flag.is_active():
        logger.info("%s is not active, cronjob will not run.", flag.name)
        return
    if not cutoff:
        last_day = datetime.date.today() - datetime.timedelta(days=1)
        cutoff = finance_utils.get_cutoff_as_datetime(last_day)
    batch = finance_api.generate_cashflows_and_payment_files(cutoff)
    if FeatureToggle.WIP_ENABLE_NEW_FINANCE_WORKFLOW:
        finance_api.generate_invoices_and_debit_notes(batch)
    elif with_invoices:
        try:
            finance_api.generate_invoices_and_debit_notes_legacy(batch)
        except finance_exceptions.NoInvoiceToGenerate:
            logger.info("Neither invoice nor debit note to generate")

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
    if settings.GENERATE_CGR_KINEPOLIS_INVOICES:
        export_csv_and_send_notification_emails_job.delay(batch.id, batch.label)


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

    if FeatureToggle.WIP_ENABLE_NEW_FINANCE_WORKFLOW:
        logger.warning(
            "Standalone `generate_invoices` command is deprecated. "
            "It's integrated in `generate_cashflows_and_payment_files` command."
        )

    try:
        finance_api.generate_invoices_and_debit_notes_legacy(batch)
    except finance_exceptions.NoInvoiceToGenerate:
        logger.info("Neither invoice nor debit note to generate")

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
    export_csv_and_send_notification_emails_job.delay(batch_id, batch.label)


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
    *,
    valid_until: str | None = None,
    force: bool = False,
) -> None:
    """Add a custom reimbursement rule that is linked to an offer."""
    offer_original_amount = decimal.Decimal(offer_original_amount.replace(",", "."))  # type: ignore[assignment]
    reimbursed_amount = decimal.Decimal(reimbursed_amount.replace(",", "."))  # type: ignore[assignment]

    offer = (
        offers_models.Offer.query.options(
            sa_orm.joinedload(offers_models.Offer.stocks, innerjoin=True),
            sa_orm.joinedload(offers_models.Offer.venue, innerjoin=True),
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


# TODO: Remove this command when recredit_users replaces recredit_underage_users in passculture-deployement
@blueprint.cli.command("recredit_underage_users")
@cron_decorators.log_cron_with_transaction
def recredit_underage_users() -> None:
    finance_api.recredit_users()


@blueprint.cli.command("recredit_users")
@cron_decorators.log_cron_with_transaction
def recredit_users() -> None:
    finance_api.recredit_users()


@blueprint.cli.command("import_ds_bank_information_applications")
@click.option(
    "--ignore_previous",
    type=bool,
    is_flag=True,
    default=False,
    help="Import all application ignoring previous import date",
)
@click.option(
    "--since",
    help="Force previous import date to this date. Format: YYYY-MM-DD. Example: 2024-01-01. Default: None.",
    type=str,
)
@cron_decorators.log_cron_with_transaction
def import_ds_bank_information_applications(ignore_previous: bool = False, since: str | None = None) -> None:
    procedures = [
        settings.DS_BANK_ACCOUNT_PROCEDURE_ID,
    ]
    forced_since = datetime.datetime.fromisoformat(since) if since else None
    for procedure in procedures:
        if not procedure:
            logger.info("Skipping DS %s because procedure id is empty", procedure)
            continue
        import_ds_applications(
            int(procedure),
            ds.update_ds_applications_for_procedure,
            ignore_previous=ignore_previous,
            forced_since=forced_since,
        )


@blueprint.cli.command("push_bank_accounts")
@click.option(
    "--count",
    help="Number of BankAccounts to sync. Default = 100. Put 0 to push all unsynced BankAccounts",
    type=int,
    default=100,
)
@cron_decorators.log_cron_with_transaction
def push_bank_accounts(count: int) -> None:
    if not FeatureToggle.ENABLE_BANK_ACCOUNT_SYNC:
        logger.info("Sync bank account cronjob will not run. ENABLE_BANK_ACCOUNT_SYNC feature must be activated")
        return

    finance_external.push_bank_accounts(count)


@blueprint.cli.command("push_invoices")
@click.option(
    "--count",
    help="Number of Invoices to sync. Default = 100. Put 0 to push all Invoices with `PENDING` status",
    type=int,
    default=100,
)
@cron_decorators.log_cron_with_transaction
def push_invoices(count: int) -> None:
    if not FeatureToggle.WIP_ENABLE_NEW_FINANCE_WORKFLOW or not FeatureToggle.ENABLE_INVOICE_SYNC:
        logger.info(
            "Sync invoice cronjob with not run. "
            "Both WIP_ENABLE_NEW_FINANCE_WORKFLOW and ENABLE_INVOICE_SYNC feature must be activated"
        )
        return

    finance_external.push_invoices(count)
