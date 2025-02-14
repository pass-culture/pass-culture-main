import itertools
import logging
import pathlib
import typing

from flask_sqlalchemy import BaseQuery
import sqlalchemy as sa
import sqlalchemy.sql.functions as sqla_func

from pcapi.core.bookings import models as bookings_models
from pcapi.core.educational import models as educational_models
from pcapi.core.finance import models
from pcapi.core.finance.api import _get_drive_folder_name
from pcapi.core.finance.api import _invoice_row_formatter
from pcapi.core.finance.api import _upload_files_to_google_drive
from pcapi.core.finance.api import _write_csv
from pcapi.core.logging import log_elapsed
from pcapi.core.offerers import models as offerers_models


logger = logging.getLogger(__name__)


def generate_specific_invoice_file(invoice_ids: list[int]) -> pathlib.Path:
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

    def get_data(query: BaseQuery, invoice_ids: typing.Iterable[int]) -> BaseQuery:
        return (
            query.join(models.Pricing.lines)
            .join(bookings_models.Booking.user)
            .join(models.Invoice.bankAccount)
            .join(models.BankAccount.offerer)
            .filter(models.Invoice.id.in_(invoice_ids))
            .group_by(
                models.Invoice.id,
                models.Invoice.date,
                models.Invoice.reference,
                models.Invoice.bankAccountId,
                models.PricingLine.category,
                offerers_models.Offerer.is_caledonian,
                bookings_models.Booking.made_by_underage_user,
            )
            .with_entities(
                models.Invoice.id,
                models.Invoice.date.label("invoice_date"),
                models.Invoice.reference.label("invoice_reference"),
                models.Invoice.bankAccountId.label("bank_account_id"),
                models.PricingLine.category.label("pricing_line_category"),
                bookings_models.Booking.made_by_underage_user.label("made_by_underage_user"),  # type: ignore[attr-defined]
                sa.case((offerers_models.Offerer.is_caledonian == True, "NC"), else_=None).label("ministry"),
                sqla_func.sum(models.PricingLine.amount).label("pricing_line_amount"),
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
            .filter(models.Invoice.id.in_(invoice_ids))
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
                sqla_func.sum(models.PricingLine.amount).label("pricing_line_amount"),
            )
        )

    indiv_query = get_data(
        models.Invoice.query.join(models.Invoice.cashflows).join(models.Cashflow.pricings).join(models.Pricing.booking),
        invoice_ids,
    )
    indiv_incident_query = get_data(
        models.Invoice.query.join(models.Invoice.cashflows)
        .join(models.Cashflow.pricings)
        .join(models.Pricing.event)
        .join(models.FinanceEvent.bookingFinanceIncident)
        .join(models.BookingFinanceIncident.booking),
        invoice_ids,
    )

    indiv_data = (
        indiv_query.union_all(indiv_incident_query)
        .group_by(
            sa.column("invoice_date"),
            sa.column("invoice_reference"),
            sa.column("bank_account_id"),
            sa.column("pricing_line_category"),
            sa.column("made_by_underage_user"),
            sa.column("ministry"),
        )
        .with_entities(
            sa.column("invoice_date"),
            sa.column("invoice_reference"),
            sa.column("bank_account_id"),
            sa.column("pricing_line_category"),
            sa.column("made_by_underage_user"),
            sa.column("ministry"),
            sqla_func.sum(sa.column("pricing_line_amount")).label("pricing_line_amount"),
        )
        .all()
    )

    collective_query = get_collective_data(
        models.Invoice.query.join(models.Invoice.cashflows)
        .join(models.Cashflow.pricings)
        .join(models.Pricing.collectiveBooking),
        invoice_ids,
    )

    collective_incident_query = get_collective_data(
        models.Invoice.query.join(models.Invoice.cashflows)
        .join(models.Cashflow.pricings)
        .join(models.Pricing.event)
        .join(models.FinanceEvent.bookingFinanceIncident)
        .join(models.BookingFinanceIncident.collectiveBooking),
        invoice_ids,
    )

    collective_data = (
        collective_query.union_all(collective_incident_query)
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
            sqla_func.sum(sa.column("pricing_line_amount")).label("pricing_line_amount"),
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
            o.made_by_underage_user,
            pricing_line_dict[o.pricing_line_category],
        ),
    )
    collective_data = sorted(
        collective_data,
        key=lambda o: (
            o.invoice_reference,
            o.ministry,
            pricing_line_dict[o.pricing_line_category],
        ),
    )

    return _write_csv(
        "invoices_with_amount_at_0",
        header,
        rows=itertools.chain(indiv_data, collective_data),
        row_formatter=_invoice_row_formatter,
        compress=True,
    )


def generate_invoice_file_for_0_euros_invoices() -> None:
    batch = models.CashflowBatch.query.filter(models.CashflowBatch.id == 2078).one()
    invoices = models.Invoice.query.filter(models.Invoice.amount == 0)
    invoice_ids = [invoice.id for invoice in invoices]
    with log_elapsed(logger, "Generated CSV invoices file"):
        path = generate_specific_invoice_file(invoice_ids)

    drive_folder_name = _get_drive_folder_name(batch)
    with log_elapsed(logger, "Uploaded CSV invoices file to Google Drive"):
        _upload_files_to_google_drive(drive_folder_name, [path])


if __name__ == "__main__":
    from pcapi.flask_app import app

    with app.app_context():
        print("Generating 0 euro invoice csv file")
        generate_invoice_file_for_0_euros_invoices()
