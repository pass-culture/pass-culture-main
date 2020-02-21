import os
import subprocess
from io import StringIO

from apscheduler.schedulers.blocking import BlockingScheduler
from flask import Flask
from mailjet_rest import Client
from sqlalchemy import orm

from models import DiscoveryView
from models.db import db
from repository.feature_queries import feature_cron_retrieve_offerers_bank_information, \
    feature_write_dashboard_enabled, \
    feature_update_booking_used, \
    feature_import_beneficiaries_enabled, \
    feature_cron_synchronize_allocine_stocks, \
    feature_update_recommendations_view, feature_cron_synchronize_libraires_stocks
from repository.provider_queries import get_provider_by_local_class
from repository.user_queries import find_most_recent_beneficiary_creation_date
from scheduled_tasks.decorators import log_cron, cron_context
from scripts.beneficiary import remote_import
from scripts.dashboard.write_dashboard import write_dashboard
from scripts.update_booking_used import update_booking_used_after_stock_occurrence
from utils.config import API_ROOT_PATH
from utils.logger import logger
from utils.mailing import MAILJET_API_KEY, MAILJET_API_SECRET

app = Flask(__name__, template_folder='../templates')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True
db.init_app(app)

RECO_VIEW_REFRESH_FREQUENCY = os.environ.get('RECO_VIEW_REFRESH_FREQUENCY', '*')


@log_cron
@cron_context
def pc_generate_and_send_payments(app, payment_message_id: str = None):
    from scripts.payment.batch import generate_and_send_payments
    app.mailjet_client = Client(auth=(MAILJET_API_KEY, MAILJET_API_SECRET), version='v3')
    generate_and_send_payments(payment_message_id)


@log_cron
@cron_context
def pc_update_booking_used(app):
    update_booking_used_after_stock_occurrence()


@log_cron
@cron_context
def pc_synchronize_allocine_stocks(app):
    allocine_stocks_provider_id = get_provider_by_local_class("AllocineStocks").id
    process = subprocess.Popen(
        f'PYTHONPATH="." python scripts/pc.py update_providables_by_provider_id'
        f' --provider-id {allocine_stocks_provider_id}',
        shell=True,
        cwd=API_ROOT_PATH)
    output, error = process.communicate()
    logger.info(StringIO(output))
    logger.info(StringIO(error))


@log_cron
@cron_context
def pc_synchronize_libraires_stocks(app):
    libraires_stocks_provider_id = get_provider_by_local_class("LibrairesStocks").id
    process = subprocess.Popen(
        f'PYTHONPATH="." python scripts/pc.py update_providables_by_provider_id'
        f' --provider-id {libraires_stocks_provider_id}',
        shell=True,
        cwd=API_ROOT_PATH)
    output, error = process.communicate()
    logger.info(StringIO(output))
    logger.info(StringIO(error))


@log_cron
@cron_context
def pc_retrieve_offerers_bank_information(app):
    process = subprocess.Popen('PYTHONPATH="." python scripts/pc.py update_providables'
                               + ' --provider BankInformationProvider',
                               shell=True,
                               cwd=API_ROOT_PATH)
    output, error = process.communicate()
    logger.info(StringIO(output))
    logger.info(StringIO(error))


@log_cron
@cron_context
def pc_remote_import_beneficiaries(app):
    app.mailjet_client = Client(auth=(MAILJET_API_KEY, MAILJET_API_SECRET), version='v3')
    import_from_date = find_most_recent_beneficiary_creation_date()
    remote_import.run(import_from_date)


@log_cron
@cron_context
def pc_write_dashboard(app):
    write_dashboard()


@log_cron
@cron_context
def pc_update_recommendations_view(app):
    DiscoveryView.refresh()


if __name__ == '__main__':
    orm.configure_mappers()
    scheduler = BlockingScheduler()

    if feature_cron_synchronize_libraires_stocks():
        scheduler.add_job(pc_synchronize_libraires_stocks, 'cron',
                          [app],
                          id='synchronize_libraire_stocks',
                          day='*', hour='21')

    if feature_cron_retrieve_offerers_bank_information():
        scheduler.add_job(pc_retrieve_offerers_bank_information, 'cron',
                          [app],
                          id='retrieve_offerers_bank_information',
                          day='*')

    if feature_cron_synchronize_allocine_stocks():
        scheduler.add_job(pc_synchronize_allocine_stocks, 'cron',
                          [app],
                          id='synchronize_allocine_stocks',
                          day='*', hour='23')

    if feature_cron_synchronize_libraires_stocks():
        scheduler.add_job(pc_synchronize_libraires_stocks, 'cron',
                          [app],
                          id='synchronize_libraires_stocks',
                          day='*', hour='22')

    if feature_import_beneficiaries_enabled():
        scheduler.add_job(pc_remote_import_beneficiaries, 'cron',
                          [app],
                          id='remote_import_beneficiaries',
                          day='*')

    if feature_write_dashboard_enabled():
        scheduler.add_job(pc_write_dashboard, 'cron',
                          [app],
                          id='pc_write_dashboard',
                          day='*', hour='4')

    if feature_update_booking_used():
        scheduler.add_job(pc_update_booking_used, 'cron',
                          [app],
                          id='pc_update_booking_used',
                          day='*', hour='0')

    if feature_update_recommendations_view():
        scheduler.add_job(pc_update_recommendations_view, 'cron',
                          [app],
                          id='pc_update_recommendations_view',
                          minute=RECO_VIEW_REFRESH_FREQUENCY)

    scheduler.start()
