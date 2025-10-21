import logging
import time

from flask import current_app as app

from pcapi import settings
from pcapi.core.finance import api as finance_api
from pcapi.core.finance import backend as finance_backend
from pcapi.core.finance import conf
from pcapi.core.finance import models as finance_models
from pcapi.models import db
from pcapi.notifications.internal import send_internal_message
from pcapi.scripts.pro.upload_reimbursement_csv_to_offerer_drive import export_csv_and_send_notification_emails
from pcapi.utils import date as date_utils


logger = logging.getLogger(__name__)


def push_bank_accounts(count: int) -> None:
    if bool(app.redis_client.exists(conf.REDIS_PUSH_BANK_ACCOUNT_LOCK)):
        return

    bank_accounts_query = (
        db.session.query(finance_models.BankAccount)
        .filter(
            finance_models.BankAccount.lastCegidSyncDate.is_(None),
            finance_models.BankAccount.status == finance_models.BankAccountApplicationStatus.ACCEPTED,
        )
        .with_entities(finance_models.BankAccount.id)
    )
    if count != 0:
        bank_accounts_query = bank_accounts_query.limit(count)

    bank_accounts = bank_accounts_query.all()

    if not bank_accounts:
        return

    app.redis_client.set(conf.REDIS_PUSH_BANK_ACCOUNT_LOCK, "1", ex=conf.REDIS_PUSH_BANK_ACCOUNT_LOCK_TIMEOUT)

    try:
        bank_account_ids = [e[0] for e in bank_accounts]
        for bank_account_id in bank_account_ids:
            try:
                backend_name = finance_backend.get_backend_name()
                logger.info("Push bank account", extra={"bank_account_id": bank_account_id, "backend": backend_name})
                finance_backend.push_bank_account(bank_account_id)
            except Exception as exc:
                logger.exception(
                    "Unable to sync bank account",
                    extra={
                        "bank_account_id": bank_account_id,
                        "exc": str(exc),
                    },
                )
                # Wait until next cron run to continue sync process
                break
            else:
                db.session.query(finance_models.BankAccount).filter(
                    finance_models.BankAccount.id == bank_account_id
                ).update(
                    {"lastCegidSyncDate": date_utils.get_naive_utc_now()},
                    synchronize_session=False,
                )
                db.session.commit()
                time_to_sleep = finance_backend.get_time_to_sleep_between_two_sync_requests()
                time.sleep(time_to_sleep)
    finally:
        app.redis_client.delete(conf.REDIS_PUSH_BANK_ACCOUNT_LOCK)


def push_invoices(count: int) -> None:
    if bool(app.redis_client.exists(conf.REDIS_PUSH_INVOICE_LOCK)):
        return

    invoices_query = (
        db.session.query(finance_models.Invoice)
        .filter(
            finance_models.Invoice.status == finance_models.InvoiceStatus.PENDING,
        )
        .with_entities(finance_models.Invoice.id)
    )
    if count != 0:
        invoices_query = invoices_query.limit(count)

    invoices = invoices_query.all()

    if not invoices:
        return

    app.redis_client.set(conf.REDIS_PUSH_INVOICE_LOCK, "1", ex=conf.REDIS_PUSH_INVOICE_LOCK_TIMEOUT)

    invoice_ids = [e[0] for e in invoices]
    encountered_error = False

    try:
        for invoice_id in invoice_ids:
            try:
                backend_name = finance_backend.get_backend_name()
                logger.info("Push invoice", extra={"invoice_id": invoice_id, "backend": backend_name})
                finance_backend.push_invoice(invoice_id)
            except Exception as exc:
                logger.exception(
                    "Unable to push invoice",
                    extra={
                        "invoice_id": invoice_id,
                        "exc": str(exc),
                    },
                )
                # Wait until next cron run to continue sync process
                encountered_error = True
                break
            else:
                db.session.query(finance_models.Invoice).filter(finance_models.Invoice.id == invoice_id).update(
                    {"status": finance_models.InvoiceStatus.PENDING_PAYMENT},
                    synchronize_session=False,
                )
                # TODO We validate whether cegid succeeds in doing the payment or not for now.
                # Later, validate_invoice will only be called in case of success
                finance_api.validate_invoice(invoice_id)
                db.session.commit()
                time_to_sleep = finance_backend.get_time_to_sleep_between_two_sync_requests()
                time.sleep(time_to_sleep)
    finally:
        app.redis_client.delete(conf.REDIS_PUSH_INVOICE_LOCK)

        if not encountered_error:
            cashflow = (
                db.session.query(finance_models.Cashflow)
                .join(finance_models.Cashflow.invoices)
                .filter(finance_models.Invoice.id.in_(invoice_ids))
                .order_by(finance_models.Invoice.id)
                .limit(1)
                .one()
            )
            batch = cashflow.batch
            if settings.GENERATE_CGR_KINEPOLIS_INVOICES:
                export_csv_and_send_notification_emails(batch.id, batch.label)

            if settings.SLACK_GENERATE_INVOICES_FINISHED_CHANNEL:
                send_internal_message(
                    channel=settings.SLACK_GENERATE_INVOICES_FINISHED_CHANNEL,
                    blocks=[
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"L'envoi des factures du ({batch.label}) sur l'outil comptable est terminé avec succès",
                            },
                        }
                    ],
                    icon_emoji=":large_green_circle:",
                )
