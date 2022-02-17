import logging

import click

from pcapi.scripts.payment.banishment import do_ban_payments
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)


@blueprint.cli.command("ban_payments")
@click.option("--message-id", required=True, help="Identifiant du message (XML) ciblé")
@click.option(
    "--payment-ids",
    required=True,
    help="Identifiants des paiements à bannir séparés par des virgules",
)
def ban_payments(message_id: str, payment_ids: str):
    try:
        payment_ids = [int(payment_id) for payment_id in payment_ids]
    except ValueError:
        logger.exception('Les identifiants de paiement doivent être au format "111,222,333"')
    else:
        do_ban_payments(message_id, payment_ids)
