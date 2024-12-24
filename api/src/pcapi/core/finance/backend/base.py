import calendar
import datetime

from flask_sqlalchemy import BaseQuery
import sqlalchemy as sa
import sqlalchemy.sql.functions as sqla_func

from pcapi.core.bookings import models as bookings_models
from pcapi.core.educational import models as educational_models
from pcapi.core.finance import models as finance_models
from pcapi.core.finance.enum import DepositType


INVOICE_LINE_INDIV_DICT = {
    (finance_models.PricingLineCategory.OFFERER_REVENUE, DepositType.GRANT_18): "ORINDGRANT_18",
    (finance_models.PricingLineCategory.OFFERER_CONTRIBUTION, DepositType.GRANT_18): "OCINDGRANT_18",
    (finance_models.PricingLineCategory.COMMERCIAL_GESTURE, DepositType.GRANT_18): "CGINDGRANT_18",
    (finance_models.PricingLineCategory.OFFERER_REVENUE, DepositType.GRANT_15_17): "ORINDGRANT_15_17",
    (finance_models.PricingLineCategory.OFFERER_CONTRIBUTION, DepositType.GRANT_15_17): "OCINDGRANT_15_17",
    (finance_models.PricingLineCategory.COMMERCIAL_GESTURE, DepositType.GRANT_15_17): "CGINDGRANT_15_17",
}

INVOICE_LINE_COLLECTIVE_DICT = {
    (
        finance_models.PricingLineCategory.OFFERER_REVENUE,
        educational_models.Ministry.EDUCATION_NATIONALE.name,
    ): "ORCOLEDUC_NAT",
    (
        finance_models.PricingLineCategory.COMMERCIAL_GESTURE,
        educational_models.Ministry.EDUCATION_NATIONALE.name,
    ): "CGCOLEDUC_NAT",
    (finance_models.PricingLineCategory.OFFERER_REVENUE, educational_models.Ministry.AGRICULTURE.name): "ORCOLAGRI",
    (finance_models.PricingLineCategory.COMMERCIAL_GESTURE, educational_models.Ministry.AGRICULTURE.name): "CGCOLAGRI",
    (finance_models.PricingLineCategory.OFFERER_REVENUE, educational_models.Ministry.MER.name): "ORCOLMER",
    (finance_models.PricingLineCategory.COMMERCIAL_GESTURE, educational_models.Ministry.MER.name): "CGCOLMER",
    (finance_models.PricingLineCategory.OFFERER_REVENUE, educational_models.Ministry.ARMEES.name): "ORCOLARMEES",
    (finance_models.PricingLineCategory.COMMERCIAL_GESTURE, educational_models.Ministry.ARMEES.name): "CGCOLARMEES",
    (finance_models.PricingLineCategory.OFFERER_REVENUE, educational_models.PROGRAM_MARSEILLE_EN_GRAND): "ORCOLMEG",
    (finance_models.PricingLineCategory.COMMERCIAL_GESTURE, educational_models.PROGRAM_MARSEILLE_EN_GRAND): "CGCOLMEG",
}

TITLES = {
    "ORINDGRANT_18": "Réservations",
    "OCINDGRANT_18": "Réservations",
    "CGINDGRANT_18": "Gestes commerciaux",
    "ORINDGRANT_15_17": "Réservations",
    "OCINDGRANT_15_17": "Réservations",
    "CGINDGRANT_15_17": "Gestes commerciaux",
    "ORCOLEDUC_NAT": "Réservations",
    "CGCOLEDUC_NAT": "Gestes commerciaux",
    "ORCOLAGRI": "Réservations",
    "CGCOLAGRI": "Gestes commerciaux",
    "ORCOLARMEES": "Réservations",
    "CGCOLARMEES": "Gestes commerciaux",
    "ORCOLMER": "Réservations",
    "CGCOLMER": "Gestes commerciaux",
    "ORCOLMEG": "Réservations",
    "CGCOLMEG": "Gestes commerciaux",
}


class BaseFinanceBackend:
    @staticmethod
    def _get_invoice_daterange(invoice_date: datetime.datetime) -> tuple[datetime.date, datetime.date]:
        if invoice_date.day < 15:
            return invoice_date.replace(day=1).date(), invoice_date.replace(day=15).date()
        last_day_of_the_month = calendar.monthrange(invoice_date.year, invoice_date.month)[1]
        return invoice_date.replace(day=16).date(), invoice_date.replace(day=last_day_of_the_month)

    def get_invoice_lines(self, invoice: finance_models.Invoice) -> list[dict]:
        invoice_id = invoice.id

        indiv_data = self._get_indiv_data(
            invoice_id,
            finance_models.PricingLine.query.join(finance_models.PricingLine.pricing).join(
                finance_models.Pricing.booking
            ),
        )
        indiv_incident_data = self._get_indiv_data(
            invoice_id,
            finance_models.PricingLine.query.join(finance_models.PricingLine.pricing)
            .join(finance_models.Pricing.event)
            .join(finance_models.FinanceEvent.bookingFinanceIncident)
            .join(finance_models.BookingFinanceIncident.incident)
            .join(finance_models.BookingFinanceIncident.booking),
        )

        collective_data = self._get_collective_data(
            invoice_id,
            finance_models.PricingLine.query.join(finance_models.PricingLine.pricing).join(
                finance_models.Pricing.collectiveBooking
            ),
        )
        collective_incident_data = self._get_collective_data(
            invoice_id,
            finance_models.PricingLine.query.join(finance_models.PricingLine.pricing)
            .join(finance_models.Pricing.event)
            .join(finance_models.FinanceEvent.bookingFinanceIncident)
            .join(finance_models.BookingFinanceIncident.collectiveBooking),
        )

        return indiv_data + indiv_incident_data + collective_data + collective_incident_data

    def _get_indiv_data(self, invoice_id: int, query: BaseQuery) -> list[dict]:
        res = []
        data = (
            query.join(bookings_models.Booking.deposit)
            .filter(
                finance_models.Pricing.status == finance_models.PricingStatus.PROCESSED,
                finance_models.Invoice.id == invoice_id,
            )
            .join(finance_models.Pricing.cashflows)
            .join(finance_models.Cashflow.invoices)
            .group_by(
                finance_models.PricingLine.category,
                finance_models.Deposit.type,
            )
            .with_entities(
                finance_models.PricingLine.category.label("pricing_category"),
                finance_models.Deposit.type.label("deposit_type"),
                sqla_func.sum(finance_models.PricingLine.amount).label("pricing_amount"),
            )
            .all()
        )
        for entry in data:
            product_id = INVOICE_LINE_INDIV_DICT[(entry.pricing_category, entry.deposit_type)]
            res.append(
                {
                    "product_id": product_id,
                    "amount": -entry.pricing_amount,
                    "title": TITLES[product_id],
                }
            )
        return res

    def _get_collective_data(self, invoice_id: int, query: BaseQuery) -> list[dict]:
        res = []
        data = (
            query.join(educational_models.CollectiveBooking.collectiveStock)
            .filter(
                finance_models.Pricing.status == finance_models.PricingStatus.PROCESSED,
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
            .outerjoin(educational_models.EducationalInstitution.programs)
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
                sqla_func.sum(finance_models.PricingLine.amount).label("pricing_amount"),
            )
            .all()
        )
        for entry in data:
            product_id = INVOICE_LINE_COLLECTIVE_DICT[(entry.pricing_category, entry.ministry)]
            res.append(
                {
                    "product_id": product_id,
                    "amount": -entry.pricing_amount,
                    "title": TITLES[product_id],
                }
            )
        return res

    def push_invoice(self, invoice: finance_models.Invoice) -> dict | None:
        raise NotImplementedError()

    def push_bank_account(self, bank_account: finance_models.BankAccount) -> dict | None:
        raise NotImplementedError()

    def get_bank_account(self, bank_account_id: int) -> dict | None:
        raise NotImplementedError()

    def get_invoice(self, reference: str) -> dict | None:
        raise NotImplementedError()

    @property
    def is_configured(self) -> bool:
        raise NotImplementedError()

    @property
    def is_default(self) -> bool:
        return False

    @property
    def time_to_sleep_between_two_sync_requests(self) -> int:
        """
        Time in seconds to sleep between two requests to avoid rate limit errors
        """
        return 0
