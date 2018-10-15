import os
import traceback
from pprint import pprint
from typing import List

from flask import current_app as app

from domain.admin_emails import send_payment_transaction_email
from domain.payments import filter_out_already_paid_for_bookings, create_payment_for_booking, generate_transaction_file, \
    validate_transaction_file
from domain.reimbursement import find_all_booking_reimbursement
from models import Offerer, PcObject
from models.payment import Payment
from repository.booking_queries import find_final_offerer_bookings
from utils.logger import logger

iban = os.environ.get('PASS_CULTURE_IBAN')
bic = os.environ.get('PASS_CULTURE_BIC')


def generate_and_send_payments():
    try:
        payments = do_generate_payments()
        do_send_payments(payments, iban, bic)
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


def do_send_payments(payments: List[Payment], pass_culture_iban: str, pass_culture_bic: str) -> None:
    if not pass_culture_iban or not pass_culture_bic:
        logger.error('Missing PASS_CULTURE_IBAN[%s] or PASS_CULTURE_BIC[%s] in environment variables' % (
            pass_culture_iban, pass_culture_bic))
    else:
        file = generate_transaction_file(payments, pass_culture_iban, pass_culture_bic)
        validate_transaction_file(file)
        send_payment_transaction_email(file, app.mailjet_client.send.create)
