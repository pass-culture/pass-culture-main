"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=pc-43774-test-cegid-upgrade \
  -f NAMESPACE=cegid_test_push_invoices \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging
import time

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
import sqlalchemy.sql.functions as sa_func

from pcapi import settings
from pcapi.core.bookings import models as bookings_models
from pcapi.core.educational import models as educational_models
from pcapi.core.finance import backend as finance_backend
from pcapi.core.finance import models as finance_models
from pcapi.core.finance import utils as finance_utils
from pcapi.core.finance.backend.base import INVOICE_LINE_COLLECTIVE_DICT
from pcapi.core.finance.backend.base import INVOICE_LINE_INDIV_DICT
from pcapi.core.finance.backend.base import TITLES
from pcapi.core.finance.backend.base import ExternalType
from pcapi.core.finance.backend.base import InvoicePayload
from pcapi.core.finance.backend.cegid import CegidFinanceBackend
from pcapi.models import db


logger = logging.getLogger(__name__)


class CegidSandboxFinanceBackend(CegidFinanceBackend):
    def __init__(self) -> None:
        self._base_url = "https://xrp-flex.cegid.cloud/passculture_sandbox"
        self._interface = settings.CEGID_ENDPOINT

    def _get_indiv_data(self, invoice_id: int, query: sa_orm.Query) -> list[dict]:
        res = []
        data = (
            query.join(bookings_models.Booking.deposit)
            .filter(
                finance_models.Invoice.id == invoice_id,
                finance_models.Pricing.status == finance_models.PricingStatus.INVOICED,
            )
            .join(finance_models.Pricing.cashflows)
            .join(finance_models.Cashflow.invoices)
            .group_by(
                finance_models.PricingLine.category,
                bookings_models.Booking.usedRecreditType,
                finance_models.Deposit.type,
            )
            .with_entities(
                finance_models.PricingLine.category.label("pricing_category"),
                sa.func.coalesce(
                    bookings_models.Booking.usedRecreditType.cast(sa.String),
                    finance_models.Deposit.type.cast(sa.String),
                ).label("origin_of_credit"),
                sa_func.sum(finance_models.PricingLine.amount).label("pricing_amount"),
            )
            .all()
        )
        for entry in data:
            product_id = INVOICE_LINE_INDIV_DICT[(entry.pricing_category, entry.origin_of_credit)]
            res.append(
                {
                    "product_id": product_id,
                    "amount": entry.pricing_amount,
                    "title": TITLES[product_id],
                }
            )
        return res

    def _get_collective_data(self, invoice_id: int, query: sa_orm.Query) -> list[dict]:
        res = []
        data = (
            query.join(educational_models.CollectiveBooking.collectiveStock)
            .filter(
                finance_models.Invoice.id == invoice_id,
                finance_models.Pricing.status == finance_models.PricingStatus.INVOICED,
            )
            .join(finance_models.Pricing.cashflows)
            .join(finance_models.Cashflow.invoices)
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
            .outerjoin(educational_models.EducationalInstitutionProgramAssociation.program)
            .group_by(
                finance_models.PricingLine.category,
                educational_models.EducationalDeposit.ministry,
                educational_models.EducationalInstitutionProgram.id,
            )
            .with_entities(
                finance_models.PricingLine.category.label("pricing_category"),
                sa.func.coalesce(
                    educational_models.EducationalInstitutionProgram.name,
                    educational_models.EducationalDeposit.ministry.cast(sa.String),
                ).label("ministry"),
                sa_func.sum(finance_models.PricingLine.amount).label("pricing_amount"),
            )
            .all()
        )
        for entry in data:
            product_id = INVOICE_LINE_COLLECTIVE_DICT[(entry.pricing_category, entry.ministry)]
            res.append(
                {
                    "product_id": product_id,
                    "amount": entry.pricing_amount,
                    "title": TITLES[product_id],
                }
            )
        return res


def push_invoice(invoice_id: int) -> dict | None:
    invoice = db.session.get(finance_models.Invoice, invoice_id)
    assert invoice  # helps mypy

    invoice_external_type = ExternalType.ADR if invoice.reference.startswith("A") else ExternalType.INV
    invoice_batch = invoice.cashflows[0].batch
    start_date, end_date = finance_utils.get_invoice_daterange(invoice_batch.cutoff)
    invoice_description = f"{invoice_batch.label} - {start_date:%d/%m}-{end_date:%d/%m}"

    payload = InvoicePayload.build(invoice, invoice_external_type, invoice_description)
    return CegidSandboxFinanceBackend().push_invoice(payload)


def push_invoices() -> None:
    invoices = (
        db.session.query(finance_models.Invoice)
        .join(finance_models.Invoice.cashflows)
        .join(finance_models.Cashflow.batch)
        .filter(finance_models.CashflowBatch.label == "VIR170")  # Sep. 16
        .all()
    )

    if not invoices:
        logger.info("No pending invoices found")
        return

    for invoice in invoices:
        invoice_id = invoice.id
        try:
            logger.info("Push invoice", extra={"invoice_id": invoice_id, "backend": "CegidSandboxFinanceBackend"})
            push_invoice(invoice_id)
        except Exception as exc:
            logger.exception(
                "Unable to push invoice",
                extra={
                    "invoice_id": invoice_id,
                    "exc": str(exc),
                },
            )
            # Stop script execution
            break
        else:
            time_to_sleep = finance_backend.get_time_to_sleep_between_two_sync_requests()
            time.sleep(time_to_sleep)


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    push_invoices()

    logger.info("Finished")
    db.session.rollback()  # do not save anything in database
