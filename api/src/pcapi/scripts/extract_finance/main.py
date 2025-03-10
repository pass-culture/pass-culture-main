import argparse
import datetime
import logging
import os
import typing

import sqlalchemy as sa
from sqlalchemy.engine import Row
import xlsxwriter

from pcapi.app import app
from pcapi.core.bookings import models as bookings_models
from pcapi.core.educational import models as educational_models
from pcapi.core.finance import models as finance_models
from pcapi.core.finance import utils as finance_utils
from pcapi.core.offers import models as offers_models
from pcapi.models import db


logger = logging.getLogger(__name__)

CHUNK_SIZE = 1000

FINANCE_EVENT_ID_LABEL = "ID finance event"
BOOKING_ID_LABEL = "ID Réservation"
BOOKING_TYPE_LABEL = "Type de réservation"
OFFER_NAME_LABEL = "Nom de l'offre"
INVOICE_REFERENCE_LABEL = "Référence facture"
INVOICE_DATE_LABEL = "Date de facture"
BANK_ACCOUNT_ID_LABEL = "ID compte bancaire"
OFFERER_REVENUE_LABEL = "CA offreur"
OFFERER_CONTRIBUTION_LABEL = "Contribution offreur"
COMMERCIAL_GESTURE_LABEL = "Geste commercial"
OFFER_SUBCATEGORY_ID_LABEL = "ID Sous-catégorie offre"
BENEFICIARY_ID_LABEL = "ID bénéficiaire/école"
EVENT_DATE_LABEL = "Date de l'événement ou date de validation"
BATCH_LABEL = "Référence virement"
PRICING_ID_LABEL = "ID valorisation"


def _get_invoice_pricing_lines(batch_id: int) -> list[Row]:
    invoice_pricing_line_ids = (
        db.session.query(
            finance_models.Invoice.reference,
            finance_models.Invoice.date,
            finance_models.Invoice.bankAccountId.cast(sa.String).label("bank_account_id"),
            sa.func.array_agg(finance_models.PricingLine.id).label("pricing_line_ids"),
        )
        .join(finance_models.Invoice.cashflows)
        .join(finance_models.Cashflow.batch)
        .join(finance_models.Cashflow.pricings)
        .join(finance_models.Pricing.lines)
        .filter(
            finance_models.CashflowBatch.id == batch_id,
            finance_models.Pricing.status == finance_models.PricingStatus.INVOICED,
            finance_models.PricingLine.amount != 0,
        )
        .group_by(finance_models.Invoice.id)
    ).all()
    return invoice_pricing_line_ids


def _get_amount_fields(
    invoice_reference: str, invoice_date: datetime.datetime, bank_account_id: str, batch_label: str
) -> list:
    return [
        sa.func.sum(
            sa.case(
                (
                    finance_models.PricingLine.category == finance_models.PricingLineCategory.OFFERER_REVENUE,
                    -finance_models.PricingLine.amount,
                )
            )
        ).label(OFFERER_REVENUE_LABEL),
        sa.func.sum(
            sa.case(
                (
                    finance_models.PricingLine.category == finance_models.PricingLineCategory.OFFERER_CONTRIBUTION,
                    finance_models.PricingLine.amount,
                )
            )
        ).label(OFFERER_CONTRIBUTION_LABEL),
        sa.func.sum(
            sa.case(
                (
                    finance_models.PricingLine.category == finance_models.PricingLineCategory.COMMERCIAL_GESTURE,
                    -finance_models.PricingLine.amount,
                )
            )
        ).label(COMMERCIAL_GESTURE_LABEL),
        finance_models.FinanceEvent.id.label(FINANCE_EVENT_ID_LABEL),
        sa.literal_column(f"'{invoice_reference}'").label(INVOICE_REFERENCE_LABEL),
        sa.literal_column(f"'{invoice_date.isoformat()}'").label(INVOICE_DATE_LABEL),
        sa.literal_column(bank_account_id).label(BANK_ACCOUNT_ID_LABEL),
        sa.literal_column(f"'{batch_label}'").label(BATCH_LABEL),
        finance_models.Pricing.id.label(PRICING_ID_LABEL),
    ]


def _get_group_by_fields() -> list:
    return [
        FINANCE_EVENT_ID_LABEL,
        BOOKING_ID_LABEL,
        finance_models.PricingLine.category,
        BOOKING_TYPE_LABEL,
        OFFER_NAME_LABEL,
        OFFER_SUBCATEGORY_ID_LABEL,
        BENEFICIARY_ID_LABEL,
        EVENT_DATE_LABEL,
        PRICING_ID_LABEL,
    ]


def _get_amounts_for_invoice_incident_indiv(
    invoice_reference: str,
    invoice_date: datetime.datetime,
    bank_account_id: str,
    pricing_line_ids: list[int],
    batch_label: str,
) -> list[Row]:
    select_fields = _get_amount_fields(invoice_reference, invoice_date, bank_account_id, batch_label)
    group_by_fields = _get_group_by_fields()

    query = (
        db.session.query(
            *select_fields,
            finance_models.BookingFinanceIncident.bookingId.label(BOOKING_ID_LABEL),
            sa.literal_column("'INCIDENT INVDIV'").label(BOOKING_TYPE_LABEL),
            offers_models.Offer.name.label(OFFER_NAME_LABEL),
            offers_models.Offer.subcategoryId.label(OFFER_SUBCATEGORY_ID_LABEL),
            bookings_models.Booking.userId.label(BENEFICIARY_ID_LABEL),
            sa.func.coalesce(offers_models.Stock.beginningDatetime, finance_models.Pricing.valueDate).label(
                EVENT_DATE_LABEL
            ),
        )
        .join(finance_models.Pricing.lines)
        .join(finance_models.Pricing.event)
        .join(finance_models.FinanceEvent.bookingFinanceIncident)
        .join(finance_models.BookingFinanceIncident.booking)
        .join(bookings_models.Booking.stock)
        .join(offers_models.Stock.offer)
        .filter(finance_models.PricingLine.id.in_(pricing_line_ids))
        .group_by(*group_by_fields)
    )
    return query.yield_per(CHUNK_SIZE)


def _get_amounts_for_invoice_incident_eac(
    invoice_reference: str,
    invoice_date: datetime.datetime,
    bank_account_id: str,
    pricing_line_ids: list[int],
    batch_label: str,
) -> list:
    select_fields = _get_amount_fields(invoice_reference, invoice_date, bank_account_id, batch_label)
    group_by_fields = _get_group_by_fields()

    query = (
        db.session.query(
            *select_fields,
            finance_models.BookingFinanceIncident.collectiveBookingId.label(BOOKING_ID_LABEL),
            sa.literal_column("'INCIDENT EAC'").label(BOOKING_TYPE_LABEL),
            educational_models.CollectiveOffer.name.label(OFFER_NAME_LABEL),
            educational_models.CollectiveOffer.subcategoryId.label(OFFER_SUBCATEGORY_ID_LABEL),
            educational_models.CollectiveBooking.educationalInstitutionId.label(BENEFICIARY_ID_LABEL),
            finance_models.Pricing.valueDate.label(EVENT_DATE_LABEL),
        )
        .join(finance_models.Pricing.lines)
        .join(finance_models.Pricing.event)
        .join(finance_models.FinanceEvent.bookingFinanceIncident)
        .join(finance_models.BookingFinanceIncident.collectiveBooking)
        .join(educational_models.CollectiveBooking.collectiveStock)
        .join(educational_models.CollectiveStock.collectiveOffer)
        .filter(finance_models.PricingLine.id.in_(pricing_line_ids))
        .group_by(*group_by_fields)
    )
    return query.yield_per(CHUNK_SIZE)


def _get_amounts_for_invoice_indiv(
    invoice_reference: str,
    invoice_date: datetime.datetime,
    bank_account_id: str,
    pricing_line_ids: list[int],
    batch_label: str,
) -> list:
    select_fields = _get_amount_fields(invoice_reference, invoice_date, bank_account_id, batch_label)
    group_by_fields = _get_group_by_fields()

    query = (
        db.session.query(
            *select_fields,
            bookings_models.Booking.id.label(BOOKING_ID_LABEL),
            sa.literal_column("'INVDIV'").label(BOOKING_TYPE_LABEL),
            offers_models.Offer.name.label(OFFER_NAME_LABEL),
            offers_models.Offer.subcategoryId.label(OFFER_SUBCATEGORY_ID_LABEL),
            bookings_models.Booking.userId.label(BENEFICIARY_ID_LABEL),
            sa.func.coalesce(offers_models.Stock.beginningDatetime, finance_models.Pricing.valueDate).label(
                EVENT_DATE_LABEL
            ),
        )
        .join(finance_models.Pricing.lines)
        .join(finance_models.Pricing.event)
        .join(finance_models.FinanceEvent.booking)
        .join(bookings_models.Booking.stock)
        .join(offers_models.Stock.offer)
        .filter(finance_models.PricingLine.id.in_(pricing_line_ids))
        .group_by(*group_by_fields)
    )
    return query.yield_per(CHUNK_SIZE)


def _get_amounts_for_invoice_eac(
    invoice_reference: str,
    invoice_date: datetime.datetime,
    bank_account_id: str,
    pricing_line_ids: list[int],
    batch_label: str,
) -> list:
    select_fields = _get_amount_fields(invoice_reference, invoice_date, bank_account_id, batch_label)
    group_by_fields = _get_group_by_fields()

    query = (
        db.session.query(
            *select_fields,
            educational_models.CollectiveBooking.id.label(BOOKING_ID_LABEL),
            sa.literal_column("'EAC'").label(BOOKING_TYPE_LABEL),
            educational_models.CollectiveOffer.name.label(OFFER_NAME_LABEL),
            educational_models.CollectiveOffer.subcategoryId.label(OFFER_SUBCATEGORY_ID_LABEL),
            educational_models.CollectiveBooking.educationalInstitutionId.label(BENEFICIARY_ID_LABEL),
            finance_models.Pricing.valueDate.label(EVENT_DATE_LABEL),
        )
        .join(finance_models.Pricing.lines)
        .join(finance_models.Pricing.event)
        .join(finance_models.FinanceEvent.collectiveBooking)
        .join(educational_models.CollectiveBooking.collectiveStock)
        .join(educational_models.CollectiveStock.collectiveOffer)
        .filter(finance_models.PricingLine.id.in_(pricing_line_ids))
        .group_by(*group_by_fields)
    )
    return query.yield_per(CHUNK_SIZE)


def get_amounts_for_batch(batch_id: int, batch_label: str) -> typing.Generator[Row, None, None]:
    invoices = _get_invoice_pricing_lines(batch_id)

    for invoice in invoices:
        yield from _get_amounts_for_invoice_indiv(
            invoice.reference, invoice.date, invoice.bank_account_id, invoice.pricing_line_ids, batch_label
        )
        yield from _get_amounts_for_invoice_eac(
            invoice.reference, invoice.date, invoice.bank_account_id, invoice.pricing_line_ids, batch_label
        )
        yield from _get_amounts_for_invoice_incident_indiv(
            invoice.reference, invoice.date, invoice.bank_account_id, invoice.pricing_line_ids, batch_label
        )
        yield from _get_amounts_for_invoice_incident_eac(
            invoice.reference, invoice.date, invoice.bank_account_id, invoice.pricing_line_ids, batch_label
        )


def _get_batches(year: int) -> list[Row]:
    return (
        db.session.query(
            finance_models.CashflowBatch.id,
            finance_models.CashflowBatch.label,
        )
        .filter(sa.func.extract("year", finance_models.CashflowBatch.cutoff) == year)
        .all()
    )


def get_extract_data(year: int) -> typing.Generator[Row, None, None]:
    batches = _get_batches(year)
    for batch in batches:
        logger.info("Fetching transactions for batch #%s (%s)", batch.id, batch.label)
        yield from get_amounts_for_batch(batch.id, batch.label)


def extract_finance_data_to_xlsx(year: int) -> None:
    output_file = f"{os.environ['OUTPUT_DIRECTORY']}/export_finance_{year}.xlsx"
    workbook = xlsxwriter.Workbook(output_file, {"constant_memory": True})

    worksheet = workbook.add_worksheet()
    fields: list[dict] = [
        {"label": BATCH_LABEL},
        {"label": INVOICE_REFERENCE_LABEL},
        {"label": INVOICE_DATE_LABEL},
        {"label": BANK_ACCOUNT_ID_LABEL},
        {"label": OFFERER_REVENUE_LABEL, "transform": finance_utils.cents_to_full_unit},
        {"label": OFFERER_CONTRIBUTION_LABEL, "transform": finance_utils.cents_to_full_unit},
        {"label": COMMERCIAL_GESTURE_LABEL, "transform": finance_utils.cents_to_full_unit},
        {"label": FINANCE_EVENT_ID_LABEL},
        {"label": PRICING_ID_LABEL},
        {"label": BOOKING_ID_LABEL},
        {"label": BOOKING_TYPE_LABEL},
        {"label": OFFER_NAME_LABEL},
        {"label": BENEFICIARY_ID_LABEL},
        {"label": OFFER_SUBCATEGORY_ID_LABEL},
        {"label": EVENT_DATE_LABEL, "transform": lambda x: x.isoformat()},
    ]
    # Write header
    for i, field in enumerate(fields):
        worksheet.write(0, i, field["label"])

    # Write data
    for row_index, row in enumerate(get_extract_data(year), 1):
        for field_index, field in enumerate(fields):
            field_name = field["label"]
            field_value = row[field_name]
            if field_value is None:
                continue
            transform_field_value = field.get("transform") or (lambda x: x)
            field_value = transform_field_value(row[field_name])
            worksheet.write(row_index, field_index, field_value)

    workbook.close()


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, required=True)
    args = parser.parse_args()

    extract_finance_data_to_xlsx(args.year)
