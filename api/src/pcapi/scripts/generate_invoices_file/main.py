import itertools
import logging
import pathlib
import typing

from flask_sqlalchemy import BaseQuery
import sqlalchemy as sa
import sqlalchemy.sql.functions as sa_func

import pcapi.core.bookings.models as bookings_models
import pcapi.core.educational.models as educational_models
from pcapi.core.finance import api
from pcapi.core.finance import models
from pcapi.core.logging import log_elapsed
import pcapi.core.offerers.models as offerers_models


logger = logging.getLogger(__name__)


def generate_invoices_csv(batch: models.CashflowBatch) -> None:
    with log_elapsed(logger, "Generated CSV invoices file"):
        path = generate_invoice_file(batch)
    drive_folder_name = api._get_drive_folder_name(batch)
    with log_elapsed(logger, "Uploaded CSV invoices file to Google Drive"):
        api._upload_files_to_google_drive(drive_folder_name, [path])


def generate_invoice_file(batch: models.CashflowBatch) -> pathlib.Path:
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

    def get_data(query: BaseQuery, bank_accounts: typing.Iterable[int]) -> BaseQuery:
        return (
            query.join(models.Pricing.lines)
            .join(bookings_models.Booking.deposit)
            .join(models.Invoice.bankAccount)
            .join(models.BankAccount.offerer)
            .filter(
                models.Cashflow.batchId == batch.id,
                models.Invoice.bankAccountId.in_(bank_accounts),
            )
            .group_by(
                models.Invoice.id,
                models.Invoice.date,
                models.Invoice.reference,
                models.Invoice.bankAccountId,
                models.PricingLine.category,
                offerers_models.Offerer.is_caledonian,
                api.ORIGIN_OF_CREDIT_CASE,
            )
            .with_entities(
                models.Invoice.id,
                models.Invoice.date.label("invoice_date"),
                models.Invoice.reference.label("invoice_reference"),
                models.Invoice.bankAccountId.label("bank_account_id"),
                models.PricingLine.category.label("pricing_line_category"),
                api.ORIGIN_OF_CREDIT_CASE.label("origin_of_credit"),
                sa.case((offerers_models.Offerer.is_caledonian == True, "NC"), else_=None).label("ministry"),
                sa_func.sum(models.PricingLine.amount).label("pricing_line_amount"),
            )
        )

    def get_collective_data(query: BaseQuery, bank_accounts: typing.Iterable[int]) -> BaseQuery:
        return (
            query.join(models.Pricing.lines)
            .join(educational_models.CollectiveBooking.educationalInstitution)
            .join(
                educational_models.EducationalDeposit,
                sa.and_(
                    educational_models.EducationalDeposit.educationalYearId
                    == educational_models.CollectiveBooking.educationalYearId,
                    educational_models.EducationalDeposit.educationalInstitutionId
                    == educational_models.EducationalInstitution.id,
                ),
            )
            # max 1 program because of unique constraint on EducationalInstitutionProgramAssociation.institutionId
            .outerjoin(educational_models.EducationalInstitution.programs)
            .filter(
                models.Cashflow.batchId == batch.id,
                models.Invoice.bankAccountId.in_(bank_accounts),
            )
            .group_by(
                models.Invoice.id,
                models.Invoice.date,
                models.Invoice.reference,
                models.Invoice.bankAccountId,
                models.PricingLine.category,
                educational_models.EducationalDeposit.ministry,
                educational_models.EducationalInstitutionProgram.id,
            )
            .with_entities(
                models.Invoice.id,
                models.Invoice.date.label("invoice_date"),
                models.Invoice.reference.label("invoice_reference"),
                models.Invoice.bankAccountId.label("bank_account_id"),
                models.PricingLine.category.label("pricing_line_category"),
                sa.func.coalesce(
                    educational_models.EducationalInstitutionProgram.label,
                    educational_models.EducationalInstitutionProgram.name,
                    educational_models.EducationalDeposit.ministry.cast(sa.String),
                ).label("ministry"),
                sa_func.sum(models.PricingLine.amount).label("pricing_line_amount"),
            )
        )

    bank_accounts_query = (
        models.Invoice.query.with_entities(models.Invoice.bankAccountId)
        .join(models.Invoice.cashflows)
        .filter(models.Cashflow.batchId == batch.id)
    )
    bank_accounts = [i.bankAccountId for i in bank_accounts_query]
    indiv_data = []
    collective_data = []
    chunk_size = 100
    for i in range(0, len(bank_accounts), chunk_size):
        bank_accounts_chunk = bank_accounts[i : i + chunk_size]

        indiv_query = get_data(
            models.Invoice.query.join(models.Invoice.cashflows)
            .join(models.Cashflow.pricings)
            .join(models.Pricing.booking),
            bank_accounts_chunk,
        )
        indiv_incident_query = get_data(
            models.Invoice.query.join(models.Invoice.cashflows)
            .join(models.Cashflow.pricings)
            .join(models.Pricing.event)
            .join(models.FinanceEvent.bookingFinanceIncident)
            .join(models.BookingFinanceIncident.booking),
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
            models.Invoice.query.join(models.Invoice.cashflows)
            .join(models.Cashflow.pricings)
            .join(models.Pricing.collectiveBooking),
            bank_accounts_chunk,
        )

        collective_incident_query = get_collective_data(
            models.Invoice.query.join(models.Invoice.cashflows)
            .join(models.Cashflow.pricings)
            .join(models.Pricing.event)
            .join(models.FinanceEvent.bookingFinanceIncident)
            .join(models.BookingFinanceIncident.collectiveBooking),
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

    for index, category in enumerate(sorted([e.value for e in models.PricingLineCategory], reverse=True)):
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
    return api._write_csv(
        f"invoices_{batch.label}",
        header,
        rows=itertools.chain(indiv_data, collective_data),
        row_formatter=api._invoice_row_formatter,
        compress=True,
    )


if __name__ == "__main__":
    from pcapi.flask_app import app

    app.app_context().push()
    cashflow_batch = models.CashflowBatch.query.filter(models.CashflowBatch.label == "VIR135").one()
    generate_invoices_csv(cashflow_batch)
