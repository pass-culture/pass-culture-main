import os

from scripts.payment.batch_steps import generate_new_payments, concatenate_payments_with_errors_and_retries, \
    send_transactions, send_payments_report, send_payments_details, send_wallet_balances
from utils.logger import logger
from utils.mailing import parse_email_addresses

PASS_CULTURE_IBAN = os.environ.get('PASS_CULTURE_IBAN', None)
PASS_CULTURE_BIC = os.environ.get('PASS_CULTURE_BIC', None)
PASS_CULTURE_REMITTANCE_CODE = os.environ.get('PASS_CULTURE_REMITTANCE_CODE', None)
TRANSACTIONS_RECIPIENTS = parse_email_addresses(os.environ.get('TRANSACTIONS_RECIPIENTS', None))
PAYMENTS_REPORT_RECIPIENTS = parse_email_addresses(os.environ.get('PAYMENTS_REPORT_RECIPIENTS', None))
PAYMENTS_DETAILS_RECIPIENTS = parse_email_addresses(os.environ.get('PAYMENTS_DETAILS_RECIPIENTS', None))
WALLET_BALANCES_RECIPIENTS = parse_email_addresses(os.environ.get('WALLET_BALANCES_RECIPIENTS', None))


def generate_and_send_payments():
    logger.info('[BATCH][PAYMENTS] STEP 1 : generate payments')
    pending_payments, not_processable_payments = generate_new_payments()

    logger.info('[BATCH][PAYMENTS] STEP 2 : collect payments in ERROR and RETRY statuses')
    payments_to_send = concatenate_payments_with_errors_and_retries(pending_payments)

    try:
        logger.info('[BATCH][PAYMENTS] STEP 3 : send transactions')
        send_transactions(
            payments_to_send, PASS_CULTURE_IBAN, PASS_CULTURE_BIC, PASS_CULTURE_REMITTANCE_CODE, TRANSACTIONS_RECIPIENTS
        )
    except Exception as e:
        logger.error('[BATCH][PAYMENTS] STEP 3', e)

    try:
        logger.info('[BATCH][PAYMENTS] STEP 4 : send payments report')
        send_payments_report(payments_to_send + not_processable_payments, PAYMENTS_REPORT_RECIPIENTS)
    except Exception as e:
        logger.error('[BATCH][PAYMENTS] STEP 4', e)

    try:
        logger.info('[BATCH][PAYMENTS] STEP 5 : send payments details')
        send_payments_details(payments_to_send, PAYMENTS_DETAILS_RECIPIENTS)
    except Exception as e:
        logger.error('[BATCH][PAYMENTS] STEP 5', e)

    try:
        logger.info('[BATCH][PAYMENTS] STEP 6 : send wallet balances')
        send_wallet_balances(WALLET_BALANCES_RECIPIENTS)
    except Exception as e:
        logger.error('[BATCH][PAYMENTS] STEP 6', e)
