from flask import current_app as app

from pcapi.scripts.payment.batch import generate_and_send_payments


@app.manager.option(
    "-p", "--payment_id", dest="payment_message_id", required=False, help="Identifiant du paiement à rejouer"
)
def generate_payments(payment_message_id: str = None):
    generate_and_send_payments(payment_message_id)
