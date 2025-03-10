import argparse
import csv
import datetime
import logging
import os
import typing

import sqlalchemy as sa
from sqlalchemy.engine import Row

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


def _get_pricing_line_ids_for_invoice(invoice_id: int) -> list[int]:
    query = (
        db.session.query(
            finance_models.PricingLine.id,
            finance_models.PricingLine.amount,
            finance_models.Pricing.status,
        )
        .join(finance_models.PricingLine.pricing)
        .join(finance_models.Pricing.cashflows)
        .join(finance_models.Cashflow.invoices)
        .filter(finance_models.Invoice.id == invoice_id)
    ).all()
    return [
        line_id
        for line_id, line_amount, pricing_status in query
        if line_amount != 0 and pricing_status == finance_models.PricingStatus.INVOICED
    ]


def _get_invoices_with_pricing_lines(batch_id: int) -> list[dict]:
    invoices = (
        db.session.query(
            finance_models.Invoice.id,
            finance_models.Invoice.reference,
            finance_models.Invoice.date,
            finance_models.Invoice.bankAccountId,
        )
        .join(finance_models.Invoice.cashflows)
        .join(finance_models.Cashflow.batch)
        .filter(
            finance_models.CashflowBatch.id == batch_id,
        )
    ).all()

    return [
        {
            "reference": invoice.reference,
            "date": invoice.date,
            "bank_account_id": invoice.bankAccountId,
            "pricing_line_ids": _get_pricing_line_ids_for_invoice(invoice.id),
        }
        for invoice in invoices
    ]


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
        sa.literal_column(f"'{bank_account_id}'").label(BANK_ACCOUNT_ID_LABEL),
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
    invoices = _get_invoices_with_pricing_lines(batch_id)

    for invoice in invoices:
        logger.info("Fetching data for invoice %s", invoice["reference"])
        yield from _get_amounts_for_invoice_indiv(
            invoice["reference"], invoice["date"], invoice["bank_account_id"], invoice["pricing_line_ids"], batch_label
        )
        yield from _get_amounts_for_invoice_eac(
            invoice["reference"], invoice["date"], invoice["bank_account_id"], invoice["pricing_line_ids"], batch_label
        )
        yield from _get_amounts_for_invoice_incident_indiv(
            invoice["reference"], invoice["date"], invoice["bank_account_id"], invoice["pricing_line_ids"], batch_label
        )
        yield from _get_amounts_for_invoice_incident_eac(
            invoice["reference"], invoice["date"], invoice["bank_account_id"], invoice["pricing_line_ids"], batch_label
        )


def _get_batches(year: int, month: int) -> list[Row]:
    return (
        db.session.query(
            finance_models.CashflowBatch.id,
            finance_models.CashflowBatch.label,
        )
        .filter(
            sa.func.extract("year", finance_models.CashflowBatch.cutoff) == year,
            sa.func.extract("month", finance_models.CashflowBatch.cutoff) == month,
        )
        .all()
    )


def get_extract_data(year: int, month: int) -> typing.Generator[Row, None, None]:
    batches = _get_batches(year, month)
    for batch in batches:
        logger.info("Fetching transactions for batch #%s (%s)", batch.id, batch.label)
        yield from get_amounts_for_batch(batch.id, batch.label)


def extract_finance_data_to_csv(year: int) -> None:
    # os.environ["OUTPUT_DIRECTORY"] = "."

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
    for month in range(1, 13):
        output_file = f"{os.environ['OUTPUT_DIRECTORY']}/export_finance_{year}_{month:02}.csv"
        logger.info("Exporting data to %s", output_file)

        with open(output_file, "w", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=[e["label"] for e in fields])

            writer.writeheader()
            for row in get_extract_data(year, month):
                transformed_row = {}
                for field in fields:
                    field_label = field["label"]
                    transform = field.get("transform") or (lambda x: x)
                    value = row[field_label]
                    transformed_row[field_label] = transform(value) if value is not None else None
                writer.writerow(transformed_row)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, required=True)
    args = parser.parse_args()

    extract_finance_data_to_csv(args.year)
