import click

import pcapi.core.payments.utils as payments_utils
from pcapi.scripts.payment.batch import generate_and_send_payments
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)


@blueprint.cli.command("generate_payments")
@click.option("--last-day", required=True, help="Dernier jour de réservations utilisées à prendre en compte")
def generate_payments(last_day: str = None):
    """Generate payments up to and including `last_day`, as an
    ISO-formatted date.

    For example, if you want to include all bookings of May 2021, you
    must provide ``2021-06-31``.
    """
    cutoff_date = payments_utils.get_cutoff_as_datetime(last_day)
    generate_and_send_payments(cutoff_date, batch_date=None)
