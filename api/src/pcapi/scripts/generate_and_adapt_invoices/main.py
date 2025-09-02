"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/BSR-generate-invoices-the-old-way/api/src/pcapi/scripts/generate_and_adapt_invoices/main.py

"""

import datetime
import logging

import sqlalchemy as sa

from pcapi import settings
from pcapi.app import app
from pcapi.core.bookings import models as bookings_models
from pcapi.core.finance import models as finance_models
from pcapi.core.logging import log_elapsed
from pcapi.models import db
from pcapi.utils.chunks import get_chunks
from pcapi.workers.export_csv_and_send_notification_emails_job import export_csv_and_send_notification_emails_job


logger = logging.getLogger(__name__)


def adapt_invoices() -> None:
    cashflows = (
        db.session.query(finance_models.Cashflow)
        .filter(finance_models.Cashflow.status == finance_models.CashflowStatus.PENDING_ACCEPTANCE)
        .all()
    )
    cashflow_ids = [cashflow.id for cashflow in cashflows]

    # Invoice.status: PENDING -> PAID
    with log_elapsed(logger, "Updating status of invoices"):
        db.session.execute(
            sa.text(
                """
                  UPDATE invoice
                  SET status = :paid
                  WHERE status = :pending
                """
            ),
            params={
                "paid": finance_models.InvoiceStatus.PAID.value,
                "pending": finance_models.InvoiceStatus.PENDING.value,
            },
        )

    # Cashflow.status: PENDING_ACCEPTANCE -> ACCEPTED
    with log_elapsed(logger, "Updating status of cashflows"):
        db.session.execute(
            sa.text(
                """
                WITH updated AS (
                  UPDATE cashflow
                  SET status = :accepted
                  WHERE id IN :cashflow_ids
                  RETURNING id AS cashflow_id
                )
                INSERT INTO cashflow_log
                ("cashflowId", "statusBefore", "statusAfter")
                SELECT updated.cashflow_id, :pending_acceptance, :accepted FROM updated
                """
            ),
            params={
                "cashflow_ids": tuple(cashflow_ids),
                "accepted": finance_models.CashflowStatus.ACCEPTED.value,
                "pending_acceptance": finance_models.CashflowStatus.PENDING_ACCEPTANCE.value,
            },
        )

    # Pricing.status: PROCESSED -> INVOICED
    # SQLAlchemy ORM cannot call `update()` if a query has been JOINed.
    with log_elapsed(logger, "Updating status of pricings"):
        pricing_ids = (
            db.session.query(finance_models.Pricing)
            .join(finance_models.Pricing.cashflows)
            .filter(
                finance_models.Cashflow.id.in_(cashflow_ids),
            )
            .with_entities(finance_models.Pricing.id)
            .all()
        )
        pricing_ids = [p[0] for p in pricing_ids]
        for chunk in get_chunks(pricing_ids, 1000):
            db.session.execute(
                sa.text(
                    """
                    WITH updated AS (
                    UPDATE pricing
                    SET status = :invoiced
                    WHERE
                        pricing.id IN :pricing_ids
                    RETURNING id AS pricing_id
                    )
                    INSERT INTO pricing_log
                    ("pricingId", "statusBefore", "statusAfter", reason)
                    SELECT updated.pricing_id, :processed, :invoiced, :log_reason from updated
                """
                ),
                {
                    "processed": finance_models.PricingStatus.PROCESSED.value,
                    "invoiced": finance_models.PricingStatus.INVOICED.value,
                    "log_reason": finance_models.PricingLogReason.GENERATE_INVOICE.value,
                    "pricing_ids": tuple(chunk),
                },
            )

    # Booking.status: USED -> REIMBURSED (but keep CANCELLED as is)
    with log_elapsed(logger, "Updating status of individual bookings"):
        booking_ids = (
            db.session.query(finance_models.Pricing)
            .join(finance_models.Pricing.cashflows)
            .filter(
                finance_models.Cashflow.id.in_(cashflow_ids),
            )
            .with_entities(finance_models.Pricing.bookingId)
            .all()
        )
        booking_ids = [b[0] for b in booking_ids]
        for chunk in get_chunks(booking_ids, 1000):
            db.session.execute(
                sa.text(
                    """
                UPDATE booking
                SET
                  status =
                    CASE WHEN booking.status = CAST(:cancelled AS booking_status)
                    THEN CAST(:cancelled AS booking_status)
                    ELSE CAST(:reimbursed AS booking_status)
                    END,
                  "reimbursementDate" = now()
                WHERE
                  booking.id IN :booking_ids
                """
                ),
                {
                    "cancelled": bookings_models.BookingStatus.CANCELLED.value,
                    "reimbursed": bookings_models.BookingStatus.REIMBURSED.value,
                    "booking_ids": tuple(chunk),
                },
            )

    # CollectiveBooking.status: USED -> REIMBURSED (but keep CANCELLED as is)
    with log_elapsed(logger, "Updating status of collective bookings"):
        db.session.execute(
            sa.text(
                """
            UPDATE collective_booking
            SET
            status =
                CASE WHEN collective_booking.status = CAST(:cancelled AS bookingstatus)
                THEN CAST(:cancelled AS bookingstatus)
                ELSE CAST(:reimbursed AS bookingstatus)
                END,
            "reimbursementDate" = now()
            FROM pricing, cashflow_pricing
            WHERE
                collective_booking.id = pricing."collectiveBookingId"
            AND pricing.id = cashflow_pricing."pricingId"
            AND cashflow_pricing."cashflowId" IN :cashflow_ids
            """
            ),
            {
                "cancelled": bookings_models.BookingStatus.CANCELLED.value,
                "reimbursed": bookings_models.BookingStatus.REIMBURSED.value,
                "cashflow_ids": tuple(cashflow_ids),
                "reimbursement_date": datetime.datetime.utcnow(),
            },
        )

    db.session.commit()


if __name__ == "__main__":
    app.app_context().push()

    # adapt_invoices()
    batch = db.session.query(finance_models.CashflowBatch).filter(finance_models.CashflowBatch.label == "VIR145").one()
    # finance_api.generate_invoices_and_debit_notes_legacy(batch)
    if settings.GENERATE_CGR_KINEPOLIS_INVOICES:
        export_csv_and_send_notification_emails_job.delay(batch.id, batch.label)
