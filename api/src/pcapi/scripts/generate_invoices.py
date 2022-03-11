import datetime
import logging

import click

import pcapi.core.finance.api as finance_api
from pcapi.utils.blueprint import Blueprint


logger = logging.getLogger(__name__)
blueprint = Blueprint(__name__, __name__)


@blueprint.cli.command("generate_invoices")
def generate_invoices():
    """Generate (and store) all invoices.

    This command can be run multiple times.
    """
    finance_api.generate_invoices()


# FIXME (dbaty, 2022-03-11): do we really need this command?
@blueprint.cli.command("generate_invoice_file")
@click.option("-d", "--date", type=click.DateTime(formats=["%Y-%m-%d"]), default=str(datetime.date.today()))
def generate_invoice_file(date):
    """Generate a csv file containing all invoices data for a given date"""
    finance_api.generate_invoice_file(date.date())
