import datetime
import logging

import click

import pcapi.core.finance.api as finance_api
from pcapi.models.feature import FeatureToggle
from pcapi.utils.blueprint import Blueprint


logger = logging.getLogger(__name__)
blueprint = Blueprint(__name__, __name__)


@blueprint.cli.command("generate_invoices")
def generate_invoices():  # type: ignore [no-untyped-def]
    """Generate (and store) all invoices.

    This command can be run multiple times.
    """
    finance_api.generate_invoices()


# FIXME (dbaty, 2022-03-11): do we really need this command?
@blueprint.cli.command("generate_invoice_file")
@click.option("-d", "--date", type=click.DateTime(formats=["%Y-%m-%d"]), default=str(datetime.date.today()))
def generate_invoice_file(date):  # type: ignore [no-untyped-def]
    """Generate a csv file containing all invoices data for a given date"""
    use_reimbursement_point = FeatureToggle.USE_REIMBURSEMENT_POINT_FOR_CASHFLOWS.is_active()
    finance_api.generate_invoice_file(date.date(), use_reimbursement_point)
