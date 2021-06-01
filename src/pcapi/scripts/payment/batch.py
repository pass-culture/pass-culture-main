import datetime
import logging

from pcapi import settings
from pcapi.models.feature import FeatureToggle
from pcapi.models.payment_status import TransactionStatus
from pcapi.repository import feature_queries
from pcapi.repository import payment_queries
from pcapi.scripts.payment.batch_steps import generate_new_payments
from pcapi.scripts.payment.batch_steps import include_error_and_retry_payments_in_batch
from pcapi.scripts.payment.batch_steps import send_payments_details
from pcapi.scripts.payment.batch_steps import send_payments_report
from pcapi.scripts.payment.batch_steps import send_transactions
from pcapi.scripts.payment.batch_steps import send_wallet_balances
from pcapi.scripts.payment.batch_steps import set_not_processable_payments_with_bank_information_to_retry
from pcapi.scripts.update_booking_used import update_booking_used_after_stock_occurrence


logger = logging.getLogger(__name__)


def generate_and_send_payments(batch_date: datetime.datetime = None):
    logger.info("[BATCH][PAYMENTS] STEP 0 : validate bookings associated to outdated stocks")
    if feature_queries.is_active(FeatureToggle.UPDATE_BOOKING_USED):
        update_booking_used_after_stock_occurrence()

    if batch_date is None:
        batch_date = datetime.datetime.utcnow()
        generate_payments(batch_date)

    payments_to_send = payment_queries.get_payments_by_status(
        (TransactionStatus.PENDING, TransactionStatus.ERROR, TransactionStatus.RETRY), batch_date
    )

    # `send_transactions()` is called last because it updates the
    # status of the payments, which modifies what `payments_to_send`
    # yields afterwards.
    try:
        logger.info("[BATCH][PAYMENTS] STEP 3 : send transactions")
        send_transactions(
            payments_to_send,
            settings.PASS_CULTURE_IBAN,
            settings.PASS_CULTURE_BIC,
            settings.PASS_CULTURE_REMITTANCE_CODE,
            settings.TRANSACTIONS_RECIPIENTS,
        )
    except Exception as e:  # pylint: disable=broad-except
        logger.exception("[BATCH][PAYMENTS] STEP 3: %s", e)
    else:
        # We cannot use `payments_to_send` anymore because
        # `send_transactions()` updates the status of the payments, so
        # the query would not yield any result anymore.
        del payments_to_send

    try:
        logger.info("[BATCH][PAYMENTS] STEP 4 : send payments report")
        send_payments_report(batch_date, settings.PAYMENTS_REPORT_RECIPIENTS)
    except Exception as e:  # pylint: disable=broad-except
        logger.exception("[BATCH][PAYMENTS] STEP 4: %s", e)

    # Recreate `payments_to_send` query, after `send_transactions()`
    # has updated the status of all payments.
    payments_to_send = payment_queries.get_payments_by_status([TransactionStatus.UNDER_REVIEW], batch_date)
    try:
        logger.info("[BATCH][PAYMENTS] STEP 5 : send payments details")
        send_payments_details(payments_to_send, settings.PAYMENTS_DETAILS_RECIPIENTS)
    except Exception as e:  # pylint: disable=broad-except
        logger.exception("[BATCH][PAYMENTS] STEP 5: %s", e)

    try:
        logger.info("[BATCH][PAYMENTS] STEP 6 : send wallet balances")
        send_wallet_balances(settings.WALLET_BALANCES_RECIPIENTS)
    except Exception as e:  # pylint: disable=broad-except
        logger.exception("[BATCH][PAYMENTS] STEP 6: %s", e)

    logger.info("[BATCH][PAYMENTS] generate_and_send_payments is done")


def generate_payments(batch_date: datetime.datetime):
    logger.info("[BATCH][PAYMENTS] STEP 1 : generate payments")
    generate_new_payments(batch_date)

    logger.info("[BATCH][PAYMENTS] STEP 2 : set NOT_PROCESSABLE payments to RETRY")
    set_not_processable_payments_with_bank_information_to_retry(batch_date)

    logger.info("[BATCH][PAYMENTS] STEP 2 Bis : include payments in ERROR and RETRY statuses")
    include_error_and_retry_payments_in_batch(batch_date)

    by_status = payment_queries.get_payment_count_by_status(batch_date)
    total = sum(count for count in by_status.values())
    logger.info("[BATCH][PAYMENTS] %i payments in status ERROR to send", by_status.get("ERROR", 0))
    logger.info("[BATCH][PAYMENTS] %i payments in status RETRY to send", by_status.get("RETRY", 0))
    logger.info("[BATCH][PAYMENTS] %i payments in total to send", total)
