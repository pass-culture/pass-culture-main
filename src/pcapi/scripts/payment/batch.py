import os
from typing import List
from typing import Tuple

from pcapi.models import Feature
from pcapi.models.feature import FeatureToggle
from pcapi.models.payment import Payment
from pcapi.repository import feature_queries
from pcapi.repository.payment_queries import get_payments_by_message_id
from pcapi.scripts.payment.batch_steps import concatenate_payments_with_errors_and_retries
from pcapi.scripts.payment.batch_steps import generate_new_payments
from pcapi.scripts.payment.batch_steps import send_payments_details
from pcapi.scripts.payment.batch_steps import send_payments_report
from pcapi.scripts.payment.batch_steps import send_transactions
from pcapi.scripts.payment.batch_steps import send_wallet_balances
from pcapi.scripts.payment.batch_steps import set_not_processable_payments_with_bank_information_to_retry
from pcapi.scripts.update_booking_used import update_booking_used_after_stock_occurrence
from pcapi.utils.logger import logger
from pcapi.utils.mailing import parse_email_addresses


def generate_and_send_payments(payment_message_id: str = None):
    PASS_CULTURE_IBAN = os.environ.get('PASS_CULTURE_IBAN', None)
    PASS_CULTURE_BIC = os.environ.get('PASS_CULTURE_BIC', None)
    PASS_CULTURE_REMITTANCE_CODE = os.environ.get('PASS_CULTURE_REMITTANCE_CODE', None)

    TRANSACTIONS_RECIPIENTS = parse_email_addresses(os.environ.get('TRANSACTIONS_RECIPIENTS', None))
    PAYMENTS_REPORT_RECIPIENTS = parse_email_addresses(os.environ.get('PAYMENTS_REPORT_RECIPIENTS', None))
    PAYMENTS_DETAILS_RECIPIENTS = parse_email_addresses(os.environ.get('PAYMENTS_DETAILS_RECIPIENTS', None))
    WALLET_BALANCES_RECIPIENTS = parse_email_addresses(os.environ.get('WALLET_BALANCES_RECIPIENTS', None))

    logger.info('[BATCH][PAYMENTS] STEP 0 : validate bookings associated to outdated stocks')
    if feature_queries.is_active(FeatureToggle.UPDATE_BOOKING_USED):
        update_booking_used_after_stock_occurrence()

    not_processable_payments, payments_to_send = generate_or_collect_payments(payment_message_id)

    try:
        logger.info('[BATCH][PAYMENTS] STEP 3 : send transactions')
        send_transactions(
            payments_to_send, PASS_CULTURE_IBAN, PASS_CULTURE_BIC, PASS_CULTURE_REMITTANCE_CODE, TRANSACTIONS_RECIPIENTS
        )
    except Exception as e:
        logger.exception('[BATCH][PAYMENTS] STEP 3', e)

    try:
        logger.info('[BATCH][PAYMENTS] STEP 4 : send payments report')
        send_payments_report(payments_to_send + not_processable_payments, PAYMENTS_REPORT_RECIPIENTS)
    except Exception as e:
        logger.exception('[BATCH][PAYMENTS] STEP 4', e)

    try:
        logger.info('[BATCH][PAYMENTS] STEP 5 : send payments details')
        send_payments_details(payments_to_send, PAYMENTS_DETAILS_RECIPIENTS)
    except Exception as e:
        logger.exception('[BATCH][PAYMENTS] STEP 5', e)

    try:
        logger.info('[BATCH][PAYMENTS] STEP 6 : send wallet balances')
        send_wallet_balances(WALLET_BALANCES_RECIPIENTS)
    except Exception as e:
        logger.exception('[BATCH][PAYMENTS] STEP 6', e)

    logger.info('[BATCH][PAYMENTS] generate_and_send_payments is done')


def generate_or_collect_payments(payment_message_id: str = None) -> Tuple[List[Payment], List[Payment]]:
    if payment_message_id is None:
        logger.info('[BATCH][PAYMENTS] STEP 1 : generate payments')
        pending_payments, not_processable_payments = generate_new_payments()

        logger.info('[BATCH][PAYMENTS] STEP 2 : set NOT_PROCESSABLE payments to RETRY')
        set_not_processable_payments_with_bank_information_to_retry()

        logger.info('[BATCH][PAYMENTS] STEP 2 Bis : collect payments in ERROR and RETRY statuses')
        payments_to_send = concatenate_payments_with_errors_and_retries(pending_payments)
    else:
        logger.info('[BATCH][PAYMENTS] STEP 1 Bis : collect payments corresponding to payment_message_id')
        not_processable_payments = []
        payments_to_send = get_payments_by_message_id(payment_message_id)
    return not_processable_payments, payments_to_send
