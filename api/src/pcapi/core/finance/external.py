import datetime
import logging
import time

from flask import current_app as app

from pcapi import settings
from pcapi.core.finance import api as finance_api
from pcapi.core.finance import backend as finance_backend
from pcapi.core.finance import conf
from pcapi.core.finance import models as finance_models
from pcapi.core.finance.backend.base import SettlementType
from pcapi.models import db
from pcapi.notifications.internal import send_internal_message
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


def push_invoices(count: int, override_work_hours_check: bool = False) -> None:
    if bool(app.redis_client.exists(conf.REDIS_PUSH_INVOICE_LOCK)):
        logger.info(
            "push_invoices ended because of lock",
            extra={"redis_lock_value": app.redis_client.get(conf.REDIS_PUSH_INVOICE_LOCK)},
        )
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
        logger.info("No pending invoices found")
        return

    app.redis_client.set(conf.REDIS_PUSH_INVOICE_LOCK, "1", ex=conf.REDIS_PUSH_INVOICE_LOCK_TIMEOUT)

    invoice_ids = [e[0] for e in invoices]

    try:
        for invoice_id in invoice_ids:
            try:
                backend_name = finance_backend.get_backend_name()
                logger.info("Push invoice", extra={"invoice_id": invoice_id, "backend": backend_name})
                if not override_work_hours_check and not finance_backend.check_can_push_invoice():
                    logger.info(
                        "Didn't push invoice due to work hours beginning soon",
                        extra={"invoice_id": invoice_id},
                    )
                    break
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
                # TODO We validate whether cegid succeeds in doing the payment or not for now.
                # Later, validate_invoice will only be called in case of success
                finance_api.validate_invoice(invoice_id)
                db.session.commit()
                time_to_sleep = finance_backend.get_time_to_sleep_between_two_sync_requests()
                time.sleep(time_to_sleep)

        # no break, all invoices processed without error
        else:
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
                finance_api.export_provider_reimbursement_csv_and_send_notification_emails(batch)

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

    finally:
        app.redis_client.delete(conf.REDIS_PUSH_INVOICE_LOCK)


def sync_settlements(from_date: datetime.date, to_date: datetime.date) -> None:
    try:
        settlement_payloads = finance_backend.get_settlements(from_date, to_date)
    except Exception as exc:
        logger.exception(
            "Unable to get settlements",
            extra={"exc": str(exc)},
        )
        return

    settlements_by_bank_account_id: dict[str, list] = {}
    external_bank_account_ids = set()
    invoice_references = set()
    for payload in settlement_payloads:
        settlements_by_bank_account_id.setdefault(str(payload.bank_account_id), []).append(payload)
        external_bank_account_ids.add(payload.bank_account_id)
        invoice_references.add(payload.invoice_external_reference)

    # pre-load bank accounts and invoices found in payloads data
    bank_account_ids = set(
        str(id[0])
        for id in db.session.query(finance_models.BankAccount)
        .filter(finance_models.BankAccount.id.in_(external_bank_account_ids))
        .with_entities(finance_models.BankAccount.id)
        .all()
    )

    invoices = db.session.query(finance_models.Invoice).filter(finance_models.Invoice.reference.in_(invoice_references))
    invoices_dict = {invoice.reference: invoice for invoice in invoices}

    loaded_settlement_batches: dict[str, finance_models.SettlementBatch] = {}
    loaded_settlements: dict[tuple[int, str], finance_models.Settlement] = {}

    for bank_account_id in settlements_by_bank_account_id:
        if bank_account_id not in bank_account_ids:
            logger.warning(
                "No bank account found on our side for this bank account id",
                extra={"bank_account_id": bank_account_id},
            )
            continue

        bill_settlement_payloads = (
            settlement
            for settlement in settlements_by_bank_account_id[bank_account_id]
            if settlement.settlement_type == SettlementType.PAYMENT
        )

        for payload in bill_settlement_payloads:
            if payload.invoice_external_reference not in invoices_dict:
                logger.warning(
                    "No invoice found on our side for this reference",
                    extra={
                        "invoice_external_reference": payload.invoice_external_reference,
                        "bank_account_id": payload.bank_account_id,
                        "external_settlement_id": payload.external_settlement_id,
                    },
                )
                continue

            invoice = invoices_dict[payload.invoice_external_reference]

            if payload.settlement_batch_name:
                if payload.settlement_batch_name in loaded_settlement_batches:
                    settlement_batch = loaded_settlement_batches[payload.settlement_batch_name]
                else:
                    settlement_batch = get_or_create_settlement_batch(
                        payload.settlement_batch_name, payload.settlement_batch_label
                    )
                    loaded_settlement_batches[payload.settlement_batch_name] = settlement_batch
            else:
                logger.warning(
                    "No settlement batch in the payload",
                    extra={
                        "invoice_external_reference": payload.invoice_external_reference,
                        "bank_account_id": payload.bank_account_id,
                        "settlement_id": payload.external_settlement_id,
                    },
                )
                continue

            if (payload.bank_account_id, payload.external_settlement_id) in loaded_settlements:
                settlement = loaded_settlements.get((payload.bank_account_id, payload.external_settlement_id))
            else:
                settlement = (
                    db.session.query(finance_models.Settlement)
                    .filter(
                        finance_models.Settlement.externalSettlementId == payload.external_settlement_id,
                        finance_models.Settlement.bankAccountId == payload.bank_account_id,
                    )
                    .one_or_none()
                )

            if settlement:
                if invoice not in settlement.invoices:
                    settlement.invoices.append(invoice)
            else:
                settlement = finance_models.Settlement(
                    settlementDate=payload.settlement_date,
                    externalSettlementId=payload.external_settlement_id,
                    bankAccountId=payload.bank_account_id,
                    amount=payload.amount,
                    invoices=[invoice],
                    batch=settlement_batch,
                )
                db.session.add(settlement)
            loaded_settlements[(payload.bank_account_id, payload.external_settlement_id)] = settlement
            db.session.flush()

        bill_cancelling_settlement_payloads = (
            settlement
            for settlement in settlements_by_bank_account_id[bank_account_id]
            if settlement.settlement_type == SettlementType.VOIDED_PAYMENT
        )

        for payload in bill_cancelling_settlement_payloads:
            if payload.invoice_external_reference not in invoices_dict:
                logger.warning(
                    "No invoice found on our side for this reference",
                    extra={
                        "invoice_external_reference": payload.invoice_external_reference,
                        "bank_account_id": payload.bank_account_id,
                        "external_settlement_id": payload.external_settlement_id,
                    },
                )
                continue

            if (payload.bank_account_id, payload.external_settlement_id) in loaded_settlements:
                settlement = loaded_settlements.get((payload.bank_account_id, payload.external_settlement_id))
            else:
                settlement = (
                    db.session.query(finance_models.Settlement)
                    .filter(
                        finance_models.Settlement.externalSettlementId == payload.external_settlement_id,
                        finance_models.Settlement.bankAccountId == payload.bank_account_id,
                    )
                    .one_or_none()
                )

            if not settlement:
                logger.warning(
                    "No settlement to cancel found",
                    extra={
                        "bank_account_id": payload.bank_account_id,
                        "settlement_id": payload.external_settlement_id,
                    },
                )
                continue
            elif settlement.status != finance_models.SettlementStatus.REJECTED:
                settlement.status = finance_models.SettlementStatus.REJECTED
                settlement.dateRejected = date_utils.get_naive_utc_now()
                db.session.flush()

    db.session.commit()


def get_or_create_settlement_batch(batch_name: str, batch_label: str) -> finance_models.SettlementBatch:
    settlement_batch = (
        db.session.query(finance_models.SettlementBatch)
        .filter(finance_models.SettlementBatch.name == batch_name)
        .one_or_none()
    )
    if not settlement_batch:
        settlement_batch = finance_models.SettlementBatch(name=batch_name, label=batch_label)
        db.session.add(settlement_batch)
    return settlement_batch
