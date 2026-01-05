import datetime
import decimal
import logging
import signal
import sys
import time
import typing

import click
import sqlalchemy.orm as sa_orm
from flask import current_app as app

import pcapi.core.finance.api as finance_api
import pcapi.core.finance.utils as finance_utils
import pcapi.core.offers.models as offers_models
import pcapi.utils.cron as cron_decorators
import pcapi.utils.date as date_utils
from pcapi import settings
from pcapi.connectors.dms.utils import import_ds_applications
from pcapi.core.finance import conf
from pcapi.core.finance import deposit_api
from pcapi.core.finance import ds
from pcapi.core.finance import external as finance_external
from pcapi.models import db
from pcapi.models.feature import FeatureToggle
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)


@blueprint.cli.command("price_finance_events")
@cron_decorators.log_cron_with_transaction
@cron_decorators.cron_require_feature(FeatureToggle.ENABLE_RECURRENT_CRON)
@cron_decorators.cron_require_feature(FeatureToggle.PRICE_FINANCE_EVENTS)
def price_finance_events() -> None:
    """Price finance events that have recently been created."""
    finance_api.price_events()


@blueprint.cli.command("generate_cashflows_and_payment_files")
@click.option("--override-feature-flag", help="Override feature flag", is_flag=True)
@click.option("--cutoff", help="Datetime cutoff to put in UTC timezone", type=datetime.datetime, required=False)
@click.option("--without-invoices", help="Blocks invoices generation after cashflows generation", is_flag=True)
@cron_decorators.log_cron_with_transaction
def generate_cashflows_and_payment_files(
    override_feature_flag: bool, cutoff: datetime.datetime, without_invoices: bool
) -> None:
    flag = FeatureToggle.GENERATE_CASHFLOWS_BY_CRON
    if not override_feature_flag and not flag.is_active():
        logger.info("%s is not active, cronjob will not run.", flag.name)
        return
    if not cutoff:
        last_day = datetime.date.today() - datetime.timedelta(days=1)
        cutoff = finance_utils.get_cutoff_as_datetime(last_day)
    batch = finance_api.generate_cashflows_and_payment_files(cutoff)
    finance_api.generate_invoices_and_debit_notes(batch)


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
        db.session.query(offers_models.Offer)
        .options(
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


@blueprint.cli.command("recredit_users")
@cron_decorators.log_cron_with_transaction
def recredit_users() -> None:
    deposit_api.recredit_users()


@blueprint.cli.command("import_ds_bank_information_applications")
@click.option(
    "--ignore_previous",
    is_flag=True,
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


@blueprint.cli.command("mark_without_continuation_applications")
def mark_without_continuation_applications() -> None:
    ds.mark_without_continuation_applications()


@blueprint.cli.command("clean_duplicate_bank_accounts")
def clean_duplicate_bank_accounts() -> None:
    finance_api.clean_duplicate_bank_accounts()


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
@click.option(
    "--override-work-hours-check",
    help="Run push_invoices even during work hours",
    required=False,
    is_flag=True,
)
@cron_decorators.log_cron_with_transaction
def push_invoices(count: int, override_work_hours_check: bool = False) -> None:
    if not FeatureToggle.ENABLE_INVOICE_SYNC:
        logger.info("Sync invoice cronjob with not run. ENABLE_INVOICE_SYNC feature must be activated")
        return

    # in case of a pod fail unrelated to the script, we delete the lock so the restart works
    def handler(signal_number: int, stack_frame: typing.Any) -> None:
        logger.error("Rollback and delete redis lock before restarting push_invoices")
        db.session.rollback()
        time.sleep(5)
        app.redis_client.delete(conf.REDIS_PUSH_INVOICE_LOCK)
        sys.exit(1)

    signal.signal(signal.SIGTERM, handler)

    finance_external.push_invoices(count, override_work_hours_check)


@blueprint.cli.command("sync_settlements")
@cron_decorators.log_cron
def sync_settlements() -> None:
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    finance_external.sync_settlements(from_date=yesterday, to_date=yesterday)
