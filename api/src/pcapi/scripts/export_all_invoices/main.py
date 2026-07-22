"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=master \
  -f NAMESPACE=export_all_invoices \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import csv
import itertools
import logging
import os
import pathlib
import typing

import pytz
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
import sqlalchemy.sql.functions as sa_func

from pcapi.core.bookings import models as bookings_models
from pcapi.core.educational import models as educational_models
from pcapi.core.finance import models as finance_models
from pcapi.core.finance import utils as finance_utils
from pcapi.core.finance.api import ORIGIN_OF_CREDIT_CASE
from pcapi.core.finance.api import _invoice_row_formatter
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db
from pcapi.utils import date as date_utils


logger = logging.getLogger(__name__)


def main(year: int) -> pathlib.Path:
    header = [
        "Identifiant humanisé des coordonnées bancaires",
        "Identifiant des coordonnées bancaires",
        "Date du justificatif",
        "Référence du justificatif",
        "Type de ticket de facturation",
        "Type de réservation",
        "Ministère",
        "Somme des tickets de facturation",
    ]

    def get_data(query: sa_orm.Query, bank_accounts: typing.Iterable[int]) -> sa_orm.Query:
        return (
            query.join(finance_models.Pricing.lines)
            .join(bookings_models.Booking.deposit)
            .join(finance_models.Invoice.bankAccount)
            .join(finance_models.BankAccount.offerer)
            .filter(
                sa.func.extract("year", finance_models.Invoice.date) == year,
                finance_models.Invoice.bankAccountId.in_(bank_accounts),
            )
            .group_by(
                finance_models.Invoice.id,
                finance_models.Invoice.date,
                finance_models.Invoice.reference,
                finance_models.Invoice.bankAccountId,
                finance_models.PricingLine.category,
                offerers_models.Offerer.is_caledonian,
                ORIGIN_OF_CREDIT_CASE,
            )
            .with_entities(
                finance_models.Invoice.id,
                finance_models.Invoice.date.label("invoice_date"),
                finance_models.Invoice.reference.label("invoice_reference"),
                finance_models.Invoice.bankAccountId.label("bank_account_id"),
                finance_models.PricingLine.category.label("pricing_line_category"),
                ORIGIN_OF_CREDIT_CASE.label("origin_of_credit"),
                sa.case(
                    (offerers_models.Offerer.is_caledonian == True, "NC"),
                    else_=None,
                ).label("ministry"),
                sa_func.sum(finance_models.PricingLine.amount).label("pricing_line_amount"),
            )
        )

    def get_collective_data(query: sa_orm.Query, bank_accounts: typing.Iterable[int]) -> sa_orm.Query:
        return (
            query.join(finance_models.Pricing.lines)
            .join(educational_models.CollectiveBooking.collectiveStock)
            .join(educational_models.CollectiveBooking.educationalInstitution)
            .join(educational_models.CollectiveBooking.educationalDeposit)
            # max 1 program because of unique constraint on EducationalInstitutionProgramAssociation.institutionId
            .outerjoin(
                educational_models.EducationalInstitutionProgramAssociation,
                sa.and_(
                    educational_models.EducationalInstitutionProgramAssociation.institutionId
                    == educational_models.EducationalInstitution.id,
                    educational_models.EducationalInstitutionProgramAssociation.timespan.contains(
                        educational_models.CollectiveStock.startDatetime
                    ),
                ),
            )
            .outerjoin(
                educational_models.EducationalInstitutionProgramAssociation.program,
            )
            .filter(
                sa.func.extract("year", finance_models.Invoice.date) == year,
                finance_models.Invoice.bankAccountId.in_(bank_accounts),
            )
            .group_by(
                finance_models.Invoice.id,
                finance_models.Invoice.date,
                finance_models.Invoice.reference,
                finance_models.Invoice.bankAccountId,
                finance_models.PricingLine.category,
                educational_models.EducationalDeposit.ministry,
                educational_models.EducationalInstitutionProgram.id,
            )
            .with_entities(
                finance_models.Invoice.id,
                finance_models.Invoice.date.label("invoice_date"),
                finance_models.Invoice.reference.label("invoice_reference"),
                finance_models.Invoice.bankAccountId.label("bank_account_id"),
                finance_models.PricingLine.category.label("pricing_line_category"),
                sa.func.coalesce(
                    educational_models.EducationalInstitutionProgram.label,
                    educational_models.EducationalInstitutionProgram.name,
                    educational_models.EducationalDeposit.ministry.cast(sa.String),
                ).label("ministry"),
                sa_func.sum(finance_models.PricingLine.amount).label("pricing_line_amount"),
            )
        )

    bank_accounts_query = (
        db.session.query(finance_models.Invoice)
        .with_entities(finance_models.Invoice.bankAccountId)
        .filter(sa.func.extract("year", finance_models.Invoice.date) == year)
    )
    bank_accounts = [i.bankAccountId for i in bank_accounts_query]
    logger.info("Found invoices from %s bank accounts", len(bank_accounts))
    indiv_data: list = []
    collective_data: list = []
    chunk_size = 100
    for i in range(0, len(bank_accounts), chunk_size):
        logger.info("Exporting chunk %s", i)
        bank_accounts_chunk = bank_accounts[i : i + chunk_size]

        indiv_query = get_data(
            db.session.query(finance_models.Invoice)
            .join(finance_models.Invoice.cashflows)
            .join(finance_models.Cashflow.pricings)
            .join(finance_models.Pricing.booking),
            bank_accounts_chunk,
        )
        indiv_incident_query = get_data(
            db.session.query(finance_models.Invoice)
            .join(finance_models.Invoice.cashflows)
            .join(finance_models.Cashflow.pricings)
            .join(finance_models.Pricing.event)
            .join(finance_models.FinanceEvent.bookingFinanceIncident)
            .join(finance_models.BookingFinanceIncident.booking),
            bank_accounts_chunk,
        )

        indiv_data.extend(
            indiv_query.union(indiv_incident_query)
            .group_by(
                sa.column("invoice_date"),
                sa.column("invoice_reference"),
                sa.column("bank_account_id"),
                sa.column("pricing_line_category"),
                sa.column("origin_of_credit"),
                sa.column("ministry"),
            )
            .with_entities(
                sa.column("invoice_date"),
                sa.column("invoice_reference"),
                sa.column("bank_account_id"),
                sa.column("pricing_line_category"),
                sa.column("origin_of_credit"),
                sa.column("ministry"),
                sa_func.sum(sa.column("pricing_line_amount")).label("pricing_line_amount"),
            )
            .all()
        )

        collective_query = get_collective_data(
            db.session.query(finance_models.Invoice)
            .join(finance_models.Invoice.cashflows)
            .join(finance_models.Cashflow.pricings)
            .join(finance_models.Pricing.collectiveBooking),
            bank_accounts_chunk,
        )

        collective_incident_query = get_collective_data(
            db.session.query(finance_models.Invoice)
            .join(finance_models.Invoice.cashflows)
            .join(finance_models.Cashflow.pricings)
            .join(finance_models.Pricing.event)
            .join(finance_models.FinanceEvent.bookingFinanceIncident)
            .join(finance_models.BookingFinanceIncident.collectiveBooking),
            bank_accounts_chunk,
        )

        collective_data.extend(
            collective_query.union(collective_incident_query)
            .group_by(
                sa.column("invoice_date"),
                sa.column("invoice_reference"),
                sa.column("bank_account_id"),
                sa.column("pricing_line_category"),
                sa.column("ministry"),
            )
            .with_entities(
                sa.column("invoice_date"),
                sa.column("invoice_reference"),
                sa.column("bank_account_id"),
                sa.column("pricing_line_category"),
                sa.column("ministry"),
                sa_func.sum(sa.column("pricing_line_amount")).label("pricing_line_amount"),
            )
            .all()
        )

    pricing_line_dict = {}

    for index, category in enumerate(sorted([e.value for e in finance_models.PricingLineCategory], reverse=True)):
        pricing_line_dict[category] = index

    indiv_data = sorted(
        indiv_data,
        key=lambda o: (
            o.invoice_reference,
            o.origin_of_credit,
            pricing_line_dict[o.pricing_line_category],
        ),
    )
    collective_data = sorted(
        collective_data,
        key=lambda o: (o.invoice_reference, o.ministry, pricing_line_dict[o.pricing_line_category]),
    )
    return _write_csv(
        "invoices",
        header,
        rows=itertools.chain(indiv_data, collective_data),
        row_formatter=_invoice_row_formatter,
        compress=True,
    )


def _write_csv(
    filename_base: str,
    header: typing.Iterable,
    rows: typing.Iterable,
    row_formatter: typing.Callable[[typing.Iterable], typing.Iterable] = lambda row: row,
    compress: bool = False,
) -> pathlib.Path:
    local_now = pytz.utc.localize(date_utils.get_naive_utc_now()).astimezone(finance_utils.ACCOUNTING_TIMEZONE)
    filename = filename_base + local_now.strftime("_%Y%m%d_%H%M") + ".csv"
    output_directory = os.environ.get("OUTPUT_DIRECTORY") or "."
    path = pathlib.Path(output_directory) / filename
    with open(path, "w+", encoding="utf-8") as fp:
        writer = csv.writer(fp, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(header)
        if rows is not None:
            writer.writerows(row_formatter(row) for row in rows)
    return path


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, required=True)
    args = parser.parse_args()

    main(args.year)
