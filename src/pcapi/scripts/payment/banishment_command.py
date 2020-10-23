from flask import current_app as app

from pcapi.scripts.payment.banishment import do_ban_payments, parse_raw_payments_ids
from pcapi.utils.logger import logger


@app.manager.option(
    '-m',
    '--message',
    dest='message_id',
    required=True,
    help='Identifiant du message (XML) ciblé'
)
@app.manager.option(
    '-p',
    '--payments',
    dest='raw_payment_ids_to_ban',
    required=True,
    help='Identifiants des paiements à bannir séparés par des virgules'
)
def ban_payments(message_id: str, raw_payment_ids_to_ban: str):
    try:
        payment_ids_to_ban = parse_raw_payments_ids(raw_payment_ids_to_ban)
    except ValueError:
        logger.exception('Les identifiants de paiement doivent être au format "111,222,333"')
    else:
        do_ban_payments(message_id, payment_ids_to_ban)
