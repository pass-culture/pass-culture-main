import datetime
import logging
import time

from flask import current_app as app

from pcapi.core.finance import backend as finance_backend
from pcapi.core.finance import conf
from pcapi.core.finance import models as finance_models
from pcapi.models import db


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
                    {"lastCegidSyncDate": datetime.datetime.utcnow()},
                    synchronize_session=False,
                )
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

    try:
        invoice_ids = [e[0] for e in invoices]
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
                break
            else:
                db.session.query(finance_models.Invoice).filter(finance_models.Invoice.id == invoice_id).update(
                    {"status": finance_models.InvoiceStatus.PENDING_PAYMENT},
                    synchronize_session=False,
                )
                time_to_sleep = finance_backend.get_time_to_sleep_between_two_sync_requests()
                time.sleep(time_to_sleep)
    finally:
        app.redis_client.delete(conf.REDIS_PUSH_INVOICE_LOCK)
