import os
from datetime import datetime
from typing import List, Tuple

from flask import current_app as app

from domain.admin_emails import send_payment_transaction_email, send_payment_details_email, send_wallet_balances_email, \
    send_payments_report_emails
from domain.payments import filter_out_already_paid_for_bookings, create_payment_for_booking, generate_transaction_file, \
    validate_transaction_file_structure, create_all_payments_details, generate_payment_details_csv, \
    generate_wallet_balances_csv, \
    generate_payment_transaction, generate_file_checksum, group_payments_by_status, filter_out_bookings_without_cost, \
    keep_only_pending_payments, keep_only_not_processable_payments
from domain.reimbursement import find_all_booking_reimbursement
from models import Offerer, PcObject
from models.db import db
from models.payment import Payment
from models.payment_status import TransactionStatus
from repository import payment_queries
from repository.booking_queries import find_final_offerer_bookings
from repository.user_queries import get_all_users_wallet_balances
from utils.logger import logger
from utils.mailing import MailServiceException, parse_email_addresses

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

    logger.info('[BATCH][PAYMENTS] STEP 2 : collect payments in error')
    payments_to_send = concatenate_error_payments_with(pending_payments)

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


def concatenate_error_payments_with(pending_payments: List[Payment]) -> List[Payment]:
    error_payments = payment_queries.find_error_payments()
    payments = pending_payments + error_payments
    logger.info('[BATCH][PAYMENTS] %s Payments in status ERROR to send' % len(error_payments))
    logger.info('[BATCH][PAYMENTS] %s Payments in total to send' % len(payments))
    return payments


def generate_new_payments() -> Tuple[List[Payment], List[Payment]]:
    offerers = Offerer.query.all()
    all_payments = []

    for offerer in offerers:
        final_offerer_bookings = find_final_offerer_bookings(offerer.id)
        booking_reimbursements = find_all_booking_reimbursement(final_offerer_bookings)
        booking_reimbursements_to_pay = filter_out_already_paid_for_bookings(
            filter_out_bookings_without_cost(booking_reimbursements)
        )
        with db.session.no_autoflush:
            payments = list(map(create_payment_for_booking, booking_reimbursements_to_pay))

        if payments:
            PcObject.check_and_save(*payments)
            all_payments.extend(payments)
        logger.info('[BATCH][PAYMENTS] Saved %s payments for offerer : %s' % (len(payments), offerer.name))

    logger.info('[BATCH][PAYMENTS] Generated %s payments for %s offerers in total' % (len(all_payments), len(offerers)))

    pending_payments = keep_only_pending_payments(all_payments)
    not_processable_payments = keep_only_not_processable_payments(all_payments)
    logger.info('[BATCH][PAYMENTS] %s Payments in status PENDING to send' % len(pending_payments))
    return pending_payments, not_processable_payments


def send_transactions(payments: List[Payment], pass_culture_iban: str, pass_culture_bic: str,
                      pass_culture_remittance_code: str, recipients: List[str]) -> None:
    if not pass_culture_iban or not pass_culture_bic or not pass_culture_remittance_code:
        logger.error(
            '[BATCH][PAYMENTS] Missing PASS_CULTURE_IBAN[%s], PASS_CULTURE_BIC[%s] or PASS_CULTURE_REMITTANCE_CODE[%s] in environment variables' % (
                pass_culture_iban, pass_culture_bic, pass_culture_remittance_code))
    else:
        message_id = 'passCulture-SCT-%s' % datetime.strftime(datetime.utcnow(), "%Y%m%d-%H%M%S")
        xml_file = generate_transaction_file(payments, pass_culture_iban, pass_culture_bic, message_id,
                                             pass_culture_remittance_code)
        validate_transaction_file_structure(xml_file)
        checksum = generate_file_checksum(xml_file)
        transaction = generate_payment_transaction(message_id, checksum, payments)

        logger.info(
            '[BATCH][PAYMENTS] Sending file with message ID [%s] and checksum [%s]' %
            (transaction.messageId, transaction.checksum.hex())
        )
        logger.info('[BATCH][PAYMENTS] Recipients of email : %s' % recipients)

        try:
            send_payment_transaction_email(xml_file, checksum, recipients, app.mailjet_client.send.create)
        except MailServiceException as e:
            logger.error('[BATCH][PAYMENTS] Error while sending payment transaction email to MailJet', e)
            for payment in payments:
                payment.setStatus(TransactionStatus.ERROR, detail="Erreur d'envoi à MailJet")
        else:
            for payment in payments:
                payment.setStatus(TransactionStatus.SENT)
        finally:
            PcObject.check_and_save(transaction, *payments)


def send_payments_details(payments: List[Payment], recipients: List[str]) -> None:
    if not recipients:
        logger.error('[BATCH][PAYMENTS] Missing PASS_CULTURE_PAYMENTS_DETAILS_RECIPIENTS in environment variables')
    elif all(map(lambda x: x.currentStatus.status == TransactionStatus.ERROR, payments)):
        logger.warning('[BATCH][PAYMENTS] Not sending payments details as all payments have an ERROR status')
    else:
        details = create_all_payments_details(payments)
        csv = generate_payment_details_csv(details)
        logger.info('[BATCH][PAYMENTS] Sending %s details of %s payments' % (len(details), len(payments)))
        logger.info('[BATCH][PAYMENTS] Recipients of email : %s' % recipients)
        try:
            send_payment_details_email(csv, recipients, app.mailjet_client.send.create)
        except MailServiceException as e:
            logger.error('[BATCH][PAYMENTS] Error while sending payment details email to MailJet', e)


def send_wallet_balances(recipients: List[str]) -> None:
    if not recipients:
        logger.error('[BATCH][PAYMENTS] Missing PASS_CULTURE_WALLET_BALANCES_RECIPIENTS in environment variables')
    else:
        balances = get_all_users_wallet_balances()
        csv = generate_wallet_balances_csv(balances)
        logger.info('[BATCH][PAYMENTS] Sending %s wallet balances' % len(balances))
        logger.info('[BATCH][PAYMENTS] Recipients of email : %s' % recipients)
        try:
            send_wallet_balances_email(csv, recipients, app.mailjet_client.send.create)
        except MailServiceException as e:
            logger.error('[BATCH][PAYMENTS] Error while sending users wallet balances email to MailJet', e)


def send_payments_report(payments: List[Payment], recipients: List[str]) -> None:
    if payments:
        groups = group_payments_by_status(payments)

        payments_error_details = create_all_payments_details(groups['ERROR']) if 'ERROR' in groups else []
        error_csv = generate_payment_details_csv(payments_error_details)

        payments_not_processable_details = create_all_payments_details(
            groups['NOT_PROCESSABLE']) if 'NOT_PROCESSABLE' in groups else []
        not_processable_csv = generate_payment_details_csv(payments_not_processable_details)

        logger.info(
            '[BATCH][PAYMENTS] Sending report on %s payment in ERROR and %s payment NOT_PROCESSABLE'
            % (len(payments_error_details), len(payments_not_processable_details))
        )
        logger.info('[BATCH][PAYMENTS] Recipients of email : %s' % recipients)

        try:
            send_payments_report_emails(not_processable_csv, error_csv, groups, recipients,
                                        app.mailjet_client.send.create)
        except MailServiceException as e:
            logger.error('[BATCH][PAYMENTS] Error while sending payments reports to MailJet', e)
    else:
        logger.info('[BATCH][PAYMENTS] No payments to report to the pass Culture team')
