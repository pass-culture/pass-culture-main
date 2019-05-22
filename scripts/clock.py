""" clock """
import os
import subprocess
from io import StringIO

from apscheduler.schedulers.blocking import BlockingScheduler
from flask import Flask
from mailjet_rest import Client
from sqlalchemy import orm

from models.db import db
from repository.features import feature_cron_send_final_booking_recaps_enabled, feature_cron_generate_and_send_payments, \
    feature_cron_retrieve_offerers_bank_information, feature_cron_send_remedial_emails, \
    feature_import_beneficiaries_enabled
from repository.features import feature_cron_send_wallet_balances
from repository.user_queries import find_most_recent_beneficiary_creation_date
from scripts.beneficiary import remote_import
from utils.config import API_ROOT_PATH
from utils.logger import logger
from utils.mailing import MAILJET_API_KEY, MAILJET_API_SECRET
from utils.mailing import parse_email_addresses

app = Flask(__name__, template_folder='../templates')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True
db.init_app(app)


def pc_send_final_booking_recaps():
    print("[BATCH] Cron send_final_booking_recaps: START")
    with app.app_context():
        from scripts.send_final_booking_recaps import send_final_booking_recaps
        app.mailjet_client = Client(auth=(MAILJET_API_KEY, MAILJET_API_SECRET), version='v3')
        send_final_booking_recaps()

    print("[BATCH] Cron send_final_booking_recaps: END")


def pc_generate_and_send_payments():
    logger.info("[BATCH][PAYMENTS] Cron generate_and_send_payments: START")

    with app.app_context():
        from scripts.payment.batch import generate_and_send_payments
        app.mailjet_client = Client(auth=(MAILJET_API_KEY, MAILJET_API_SECRET), version='v3')
        generate_and_send_payments()

    logger.info("[BATCH][PAYMENTS] Cron generate_and_send_payments: END")


def pc_send_wallet_balances():
    logger.info("[BATCH] Cron send_wallet_balances: START")

    with app.app_context():
        from scripts.payment.batch import send_wallet_balances
        app.mailjet_client = Client(auth=(MAILJET_API_KEY, MAILJET_API_SECRET), version='v3')
        recipients = parse_email_addresses(os.environ.get('WALLET_BALANCES_RECIPIENTS', None))
        send_wallet_balances(recipients)

    logger.info("[BATCH] Cron send_wallet_balances: END")


def pc_retrieve_offerers_bank_information():
    logger.info("[BATCH][BANK INFORMATION] Cron retrieve_offerers_bank_information: START")
    with app.app_context():
        process = subprocess.Popen('PYTHONPATH="." python scripts/pc.py update_providables'
                                   + ' --provider BankInformationProvider',
                                   shell=True,
                                   cwd=API_ROOT_PATH)
        output, error = process.communicate()
        logger.info(StringIO(output))
    logger.info("[BATCH][BANK INFORMATION] Cron retrieve_offerers_bank_information: END")


def pc_send_remedial_emails():
    logger.info("[BATCH][REMEDIAL EMAILS] Cron send_remedial_emails: START")
    with app.app_context():
        from scripts.send_remedial_emails import send_remedial_emails
        app.mailjet_client = Client(auth=(MAILJET_API_KEY, MAILJET_API_SECRET), version='v3')
        send_remedial_emails()
    logger.info("[BATCH][REMEDIAL EMAILS] Cron send_remedial_emails: END")


def pc_remote_import_beneficiaries():
    logger.info("[BATCH][REMOTE IMPORT BENEFICIARIES] Cron remote_import_beneficiaries: START")
    with app.app_context():
        app.mailjet_client = Client(auth=(MAILJET_API_KEY, MAILJET_API_SECRET), version='v3')
        import_from_date = find_most_recent_beneficiary_creation_date()
        remote_import.run(import_from_date)
    logger.info("[BATCH][REMOTE IMPORT BENEFICIARIES] Cron remote_import_beneficiaries: END")


if __name__ == '__main__':
    orm.configure_mappers()
    scheduler = BlockingScheduler()

    if feature_cron_send_final_booking_recaps_enabled():
        scheduler.add_job(pc_send_final_booking_recaps, 'cron', id='send_final_booking_recaps', day='*')

    if feature_cron_generate_and_send_payments():
        scheduler.add_job(pc_generate_and_send_payments, 'cron', id='generate_and_send_payments', day='1,15')

    if feature_cron_send_wallet_balances():
        scheduler.add_job(pc_send_wallet_balances, 'cron', id='send_wallet_balances', day='1-5')

    if feature_cron_retrieve_offerers_bank_information():
        scheduler.add_job(pc_retrieve_offerers_bank_information, 'cron', id='retrieve_offerers_bank_information',
                          day='*')
    if feature_cron_send_remedial_emails():
        scheduler.add_job(pc_send_remedial_emails, 'cron', id='send_remedial_emails', minute='*/15')

    if feature_import_beneficiaries_enabled():
        scheduler.add_job(pc_remote_import_beneficiaries, 'cron', id='remote_import_beneficiaries', day='*')

    scheduler.start()
