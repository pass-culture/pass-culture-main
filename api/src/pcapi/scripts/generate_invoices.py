import logging

from flask import Blueprint

import pcapi.core.finance.api as finance_api


logger = logging.getLogger(__name__)
blueprint = Blueprint(__name__, __name__)


@blueprint.cli.command("generate_invoices")
def generate_invoices():
    """Generate (and store) all invoices.

    This command can be run multiple times.
    """
    finance_api.generate_invoices()
