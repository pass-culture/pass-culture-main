import os
import traceback
from datetime import datetime
from pprint import pprint
from typing import List

from flask import current_app as app

from domain.admin_emails import send_payment_transaction_email, send_payment_details_email
from domain.payments import filter_out_already_paid_for_bookings, create_payment_for_booking, generate_transaction_file, \
    validate_transaction_file, create_all_payments_details, generate_payment_details_csv
from domain.reimbursement import find_all_booking_reimbursement
from models import Offerer, PcObject
from models.payment import Payment
from models.payment_status import TransactionStatus
from repository.booking_queries import find_final_offerer_bookings
from utils.logger import logger
from utils.mailing import MailServiceException

PASS_CULTURE_IBAN = os.environ.get('PASS_CULTURE_IBAN', None)
PASS_CULTURE_BIC = os.environ.get('PASS_CULTURE_BIC', None)
PASS_CULTURE_REMITTANCE_CODE = os.environ.get('PASS_CULTURE_REMITTANCE_CODE', None)
PASS_CULTURE_PAYMENTS_DETAILS_RECIPIENTS = os.environ.get('PASS_CULTURE_PAYMENTS_DETAILS_RECIPIENTS', None)


def generate_and_send_payments():
    try:
        payments = do_generate_payments()
        do_send_payments(payments, PASS_CULTURE_IBAN, PASS_CULTURE_BIC, PASS_CULTURE_REMITTANCE_CODE)
        do_send_payment_details(payments, PASS_CULTURE_PAYMENTS_DETAILS_RECIPIENTS)
    except Exception as e:
        print('ERROR: ' + str(e))
        traceback.print_tb(e.__traceback__)
        pprint(vars(e))


def do_generate_payments():
    offerers = Offerer.query.all()
    print('Generating payments for %s Offerers' % len(offerers))
    all_payments = []

    for offerer in offerers:
        print('Generating payments for Offerer : %s' % offerer.name)

        final_offerer_bookings = find_final_offerer_bookings(offerer.id)
        booking_reimbursements = find_all_booking_reimbursement(final_offerer_bookings)
        booking_reimbursements_to_pay = filter_out_already_paid_for_bookings(booking_reimbursements)
        payments = list(map(create_payment_for_booking, booking_reimbursements_to_pay))
        if payments:
            PcObject.check_and_save(*payments)
            all_payments.extend(payments)
            print('Saved %s payments for Offerer : %s' % (len(payments), offerer.name))
        else:
            print('No payments to save for Offerer : %s' % offerer.name)

    return all_payments


def do_send_payments(payments: List[Payment], pass_culture_iban: str, pass_culture_bic: str,
                     pass_culture_remittance_code: str) -> None:
    if not pass_culture_iban or not pass_culture_bic or not pass_culture_remittance_code:
        logger.error(
            'Missing PASS_CULTURE_IBAN[%s], PASS_CULTURE_BIC[%s] or PASS_CULTURE_REMITTANCE_CODE[%s] in environment variables' % (
                pass_culture_iban, pass_culture_bic, pass_culture_remittance_code))
    else:
        message_id = 'passCulture-SCT-%s' % datetime.strftime(datetime.utcnow(), "%Y%m%d-%H%M%S")
        file = generate_transaction_file(payments, pass_culture_iban, pass_culture_bic, message_id,
                                         pass_culture_remittance_code)
        validate_transaction_file(file)
        try:
            send_payment_transaction_email(file, app.mailjet_client.send.create)
        except MailServiceException as e:
            for payment in payments:
                payment.nullifyTransactionIds()

            logger.error('Error while sending payment transaction email to MailJet', e)
        else:
            for payment in payments:
                payment.setStatus(TransactionStatus.SENT)
            PcObject.check_and_save(*payments)


def do_send_payment_details(payments: List[Payment], recipients: str) -> None:
    if not recipients:
        logger.error('Missing PASS_CULTURE_PAYMENTS_DETAILS_RECIPIENTS in environment variables')
    else:
        details = create_all_payments_details(payments)
        csv = generate_payment_details_csv(details)
        try:
            send_payment_details_email(csv, recipients, app.mailjet_client.send.create)
        except MailServiceException as e:
            logger.error('Error while sending payment details email to MailJet', e)


def do_send_wallet_balances(recipients: str) -> None:
    pass
