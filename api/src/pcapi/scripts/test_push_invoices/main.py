"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml   -f ENVIRONMENT=testing   -f BRANCH_NAME=BSR-test-push-invoices   -f NAMESPACE=test_push_invoices   -f SCRIPT_ARGUMENTS="";

"""

import datetime
import logging
import time

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from pcapi.app import app
from pcapi.core.bookings import models as bookings_models
from pcapi.core.educational import models as educational_models
from pcapi.core.finance import conf
from pcapi.core.finance import models as finance_models
from pcapi.core.finance.backend.base import INVOICE_LINE_COLLECTIVE_DICT
from pcapi.core.finance.backend.base import INVOICE_LINE_INDIV_DICT
from pcapi.core.finance.backend.base import TITLES
from pcapi.core.finance.backend.cegid import CegidFinanceBackend
from pcapi.models import db


logger = logging.getLogger(__name__)


class TempCegidFinanceBackend(CegidFinanceBackend):
    def _get_indiv_data(self, invoice_id: int, query: sa_orm.Query) -> list[dict]:
        res = []
        data = (
            query.join(bookings_models.Booking.deposit)
            .filter(
                # bookings_models.Booking.status == bookings_models.BookingStatus.REIMBURSED,
                finance_models.Invoice.id == invoice_id,
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
                sa.func.sum(finance_models.PricingLine.amount).label("pricing_amount"),
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
                # educational_models.CollectiveBooking.status == educational_models.CollectiveBookingStatus.REIMBURSED,
                finance_models.Invoice.id == invoice_id,
            )
            .join(finance_models.Pricing.cashflows)
            .join(finance_models.Cashflow.invoices)
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
                sa.func.sum(finance_models.PricingLine.amount).label("pricing_amount"),
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


def _push_invoices(count: int) -> None:
    if bool(app.redis_client.exists(conf.REDIS_PUSH_INVOICE_LOCK)):
        return
    invoices_query = (
        db.session.query(finance_models.Invoice)
        .filter(
            sa.or_(
                finance_models.Invoice.date >= datetime.date(2025, 10, 15),
            )
        )
        .with_entities(finance_models.Invoice.id)
    )
    if count != 0:
        invoices_query = invoices_query.limit(count)
    invoices = invoices_query.all()
    if not invoices:
        return
    app.redis_client.set(conf.REDIS_PUSH_INVOICE_LOCK, "1", ex=conf.REDIS_PUSH_INVOICE_LOCK_TIMEOUT)
    try:
        invoice_ids = [e[0] for e in invoices]
        for invoice_id in invoice_ids:
            try:
                backend = TempCegidFinanceBackend()
                logger.info("Push invoice", extra={"invoice_id": invoice_id, "backend": "TempCegidFinanceBackend"})
                invoice = db.session.query(finance_models.Invoice).filter(finance_models.Invoice.id == invoice_id).one()
                backend.push_invoice(invoice)
            except Exception as exc:
                logger.exception(
                    "Unable to push invoice",
                    extra={
                        "invoice_id": invoice_id,
                        "exc": str(exc),
                    },
                )
                # Wait until next cron run to continue sync process
                break
            else:
                db.session.commit()
                time.sleep(5)
    finally:
        app.redis_client.delete(conf.REDIS_PUSH_INVOICE_LOCK)


if __name__ == "__main__":
    app.app_context().push()
    _push_invoices(0)
