""" clock """
import os
from flask import Flask
from mailjet_rest import Client
from apscheduler.schedulers.blocking import BlockingScheduler

from models.db import db
from utils.mailing import MAILJET_API_KEY, MAILJET_API_SECRET
from utils.logger import logger

app = Flask(__name__, template_folder='../templates')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True
db.init_app(app)


def pc_send_final_booking_recaps():
    print("Cron send_final_booking_recaps: START")
    with app.app_context():
        from scripts.send_final_booking_recaps import send_final_booking_recaps
        app.mailjet_client = Client(auth=(MAILJET_API_KEY, MAILJET_API_SECRET), version='v3')
        send_final_booking_recaps()

    print("Cron send_final_booking_recaps: END")


def pc_generate_and_send_payments():
    logger.info("[BATCH][PAYMENTS] Cron generate_and_send_payments: START")

    with app.app_context():
        from scripts.payments import generate_and_send_payments
        app.mailjet_client = Client(auth=(MAILJET_API_KEY, MAILJET_API_SECRET), version='v3')
        generate_and_send_payments()

    logger.info("[BATCH][PAYMENTS] Cron generate_and_send_payments: END")


if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(pc_send_final_booking_recaps, 'cron', id='send_final_booking_recaps', day='*')
    scheduler.add_job(pc_generate_and_send_payments, 'cron', id='generate_and_send_payments', day='1,15')
    scheduler.start()
