import datetime

from flask import current_app as app

from pcapi.scripts.payment.batch import generate_and_send_payments


@app.manager.option("--batch-date", dest="batch_date", required=False, help="Date du batch du paiement à rejouer")
def generate_payments(batch_date: datetime.datetime = None):
    generate_and_send_payments(batch_date)
