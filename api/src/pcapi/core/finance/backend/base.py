import calendar
import datetime
import enum

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
import sqlalchemy.sql.functions as sa_func
from pydantic import BaseModel as BaseModelV2

from pcapi.core.bookings import models as bookings_models
from pcapi.core.educational import models as educational_models
from pcapi.core.finance import models as finance_models
from pcapi.models import db


INVOICE_LINE_INDIV_DICT = {
    (finance_models.PricingLineCategory.OFFERER_REVENUE, finance_models.DepositType.GRANT_18.name): "ORINDGRANT_18",
    (
        finance_models.PricingLineCategory.OFFERER_CONTRIBUTION,
        finance_models.DepositType.GRANT_18.name,
    ): "OCINDGRANT_18",
    (finance_models.PricingLineCategory.COMMERCIAL_GESTURE, finance_models.DepositType.GRANT_18.name): "CGINDGRANT_18",
    (
        finance_models.PricingLineCategory.OFFERER_REVENUE,
        finance_models.DepositType.GRANT_15_17.name,
    ): "ORINDGRANT_15_17",
    (
        finance_models.PricingLineCategory.OFFERER_CONTRIBUTION,
        finance_models.DepositType.GRANT_15_17.name,
    ): "OCINDGRANT_15_17",
    (
        finance_models.PricingLineCategory.COMMERCIAL_GESTURE,
        finance_models.DepositType.GRANT_15_17.name,
    ): "CGINDGRANT_15_17",
    # If the origin of credit is GRANT_17_18, it means that booking.usedRecreditType is None.
    # Thus, we are in the case of the GRANT_15_17 booking that turned in a GRANT_17_18 one
    # due to the user's birthday happening after the booking was used but before it was reimbursed.
    (
        finance_models.PricingLineCategory.OFFERER_REVENUE,
        finance_models.DepositType.GRANT_17_18.name,
    ): "ORINDGRANT_15_17",
    (
        finance_models.PricingLineCategory.OFFERER_CONTRIBUTION,
        finance_models.DepositType.GRANT_17_18.name,
    ): "OCINDGRANT_15_17",
    (
        finance_models.PricingLineCategory.COMMERCIAL_GESTURE,
        finance_models.DepositType.GRANT_17_18.name,
    ): "CGINDGRANT_15_17",
    (
        finance_models.PricingLineCategory.OFFERER_REVENUE,
        finance_models.DepositType.GRANT_FREE.name,
    ): "ORINDGRANT_FREE",
    (
        finance_models.PricingLineCategory.OFFERER_CONTRIBUTION,
        finance_models.DepositType.GRANT_FREE.name,
    ): "OCINDGRANT_FREE",
    (
        finance_models.PricingLineCategory.OFFERER_REVENUE,
        bookings_models.BookingRecreditType.RECREDIT_18.name,
    ): "ORINDGRANT_18_V3",
    (
        finance_models.PricingLineCategory.OFFERER_CONTRIBUTION,
        bookings_models.BookingRecreditType.RECREDIT_18.name,
    ): "OCINDGRANT_18_V3",
    (
        finance_models.PricingLineCategory.COMMERCIAL_GESTURE,
        bookings_models.BookingRecreditType.RECREDIT_18.name,
    ): "CGINDGRANT_18_V3",
    (
        finance_models.PricingLineCategory.OFFERER_REVENUE,
        bookings_models.BookingRecreditType.RECREDIT_17.name,
    ): "ORINDGRANT_17_V3",
    (
        finance_models.PricingLineCategory.OFFERER_CONTRIBUTION,
        bookings_models.BookingRecreditType.RECREDIT_17.name,
    ): "OCINDGRANT_17_V3",
    (
        finance_models.PricingLineCategory.COMMERCIAL_GESTURE,
        bookings_models.BookingRecreditType.RECREDIT_17.name,
    ): "CGINDGRANT_17_V3",
}

INVOICE_LINE_COLLECTIVE_DICT = {
    (
        finance_models.PricingLineCategory.OFFERER_REVENUE,
        educational_models.Ministry.EDUCATION_NATIONALE.name,
    ): "ORCOLEDUC_NAT",
    (
        finance_models.PricingLineCategory.OFFERER_CONTRIBUTION,
        educational_models.Ministry.EDUCATION_NATIONALE.name,
    ): "OCCOLEDUC_NAT",
    (
        finance_models.PricingLineCategory.COMMERCIAL_GESTURE,
        educational_models.Ministry.EDUCATION_NATIONALE.name,
    ): "CGCOLEDUC_NAT",
    (finance_models.PricingLineCategory.OFFERER_REVENUE, educational_models.Ministry.AGRICULTURE.name): "ORCOLAGRI",
    (
        finance_models.PricingLineCategory.OFFERER_CONTRIBUTION,
        educational_models.Ministry.AGRICULTURE.name,
    ): "OCCOLAGRI",
    (finance_models.PricingLineCategory.COMMERCIAL_GESTURE, educational_models.Ministry.AGRICULTURE.name): "CGCOLAGRI",
    (finance_models.PricingLineCategory.OFFERER_REVENUE, educational_models.Ministry.MER.name): "ORCOLMER",
    (finance_models.PricingLineCategory.OFFERER_CONTRIBUTION, educational_models.Ministry.MER.name): "OCCOLMER",
    (finance_models.PricingLineCategory.COMMERCIAL_GESTURE, educational_models.Ministry.MER.name): "CGCOLMER",
    (finance_models.PricingLineCategory.OFFERER_REVENUE, educational_models.Ministry.ARMEES.name): "ORCOLARMEES",
    (finance_models.PricingLineCategory.OFFERER_CONTRIBUTION, educational_models.Ministry.ARMEES.name): "OCCOLARMEES",
    (finance_models.PricingLineCategory.COMMERCIAL_GESTURE, educational_models.Ministry.ARMEES.name): "CGCOLARMEES",
    (finance_models.PricingLineCategory.OFFERER_REVENUE, educational_models.PROGRAM_MARSEILLE_EN_GRAND): "ORCOLMEG",
    (
        finance_models.PricingLineCategory.OFFERER_CONTRIBUTION,
        educational_models.PROGRAM_MARSEILLE_EN_GRAND,
    ): "OCCOLMEG",
    (finance_models.PricingLineCategory.COMMERCIAL_GESTURE, educational_models.PROGRAM_MARSEILLE_EN_GRAND): "CGCOLMEG",
}

TITLES = {
    "ORINDGRANT_18": "Réservations",
    "OCINDGRANT_18": "Réservations",
    "CGINDGRANT_18": "Gestes commerciaux",
    "ORINDGRANT_15_17": "Réservations",
    "OCINDGRANT_15_17": "Réservations",
    "CGINDGRANT_15_17": "Gestes commerciaux",
    "ORINDGRANT_18_V3": "Réservations",
    "OCINDGRANT_18_V3": "Réservations",
    "CGINDGRANT_18_V3": "Gestes commerciaux",
    "ORINDGRANT_17_V3": "Réservations",
    "OCINDGRANT_17_V3": "Réservations",
    "CGINDGRANT_17_V3": "Gestes commerciaux",
    "ORINDGRANT_FREE": "Réservations",
    "OCINDGRANT_FREE": "Réservations",
    "ORCOLEDUC_NAT": "Réservations",
    "OCCOLEDUC_NAT": "Réservations",
    "CGCOLEDUC_NAT": "Gestes commerciaux",
    "ORCOLAGRI": "Réservations",
    "OCCOLAGRI": "Réservations",
    "CGCOLAGRI": "Gestes commerciaux",
    "ORCOLARMEES": "Réservations",
    "OCCOLARMEES": "Réservations",
    "CGCOLARMEES": "Gestes commerciaux",
    "ORCOLMER": "Réservations",
    "OCCOLMER": "Réservations",
    "CGCOLMER": "Gestes commerciaux",
    "ORCOLMEG": "Réservations",
    "OCCOLMEG": "Réservations",
    "CGCOLMEG": "Gestes commerciaux",
}


class SettlementType(enum.Enum):
    PAYMENT = "Payment"
    VOIDED_PAYMENT = "Voided Payment"


class SettlementPayload(BaseModelV2):
    bank_account_id: int
    external_settlement_id: str
    invoice_external_reference: str
    settlement_type: SettlementType
    settlement_batch_name: str | None
    settlement_batch_label: str | None
    settlement_date: datetime.date
    amount: int


class BaseFinanceBackend:
    @staticmethod
    def _get_invoice_daterange(cutoff_date: datetime.datetime) -> tuple[datetime.date, datetime.date]:
        if cutoff_date.day < 16:
            return cutoff_date.replace(day=1).date(), cutoff_date.replace(day=15).date()
        last_day_of_the_month = calendar.monthrange(cutoff_date.year, cutoff_date.month)[1]
        return cutoff_date.replace(day=16).date(), cutoff_date.replace(day=last_day_of_the_month).date()

    def get_invoice_lines(self, invoice: finance_models.Invoice) -> list[dict]:
        invoice_id = invoice.id

        indiv_data = self._get_indiv_data(
            invoice_id,
            db.session.query(finance_models.PricingLine)
            .join(finance_models.PricingLine.pricing)
            .join(finance_models.Pricing.booking),
        )
        indiv_incident_data = self._get_indiv_data(
            invoice_id,
            db.session.query(finance_models.PricingLine)
            .join(finance_models.PricingLine.pricing)
            .join(finance_models.Pricing.event)
            .join(finance_models.FinanceEvent.bookingFinanceIncident)
            .join(finance_models.BookingFinanceIncident.incident)
            .join(finance_models.BookingFinanceIncident.booking),
        )

        collective_data = self._get_collective_data(
            invoice_id,
            db.session.query(finance_models.PricingLine)
            .join(finance_models.PricingLine.pricing)
            .join(finance_models.Pricing.collectiveBooking),
        )
        collective_incident_data = self._get_collective_data(
            invoice_id,
            db.session.query(finance_models.PricingLine)
            .join(finance_models.PricingLine.pricing)
            .join(finance_models.Pricing.event)
            .join(finance_models.FinanceEvent.bookingFinanceIncident)
            .join(finance_models.BookingFinanceIncident.collectiveBooking),
        )

        invoice_lines = [
            line
            for line in (indiv_data + indiv_incident_data + collective_data + collective_incident_data)
            if line["amount"] != 0
        ]

        return invoice_lines

    def _get_indiv_data(self, invoice_id: int, query: sa_orm.Query) -> list[dict]:
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
                finance_models.Pricing.status == finance_models.PricingStatus.PROCESSED,
                finance_models.Invoice.id == invoice_id,
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

    def check_can_push_invoice(self) -> bool:
        return True

    def push_invoice(self, invoice: finance_models.Invoice) -> dict | None:
        raise NotImplementedError()

    def push_bank_account(self, bank_account: finance_models.BankAccount) -> dict | None:
        raise NotImplementedError()

    def get_bank_account(self, bank_account_id: int) -> dict | None:
        raise NotImplementedError()

    def get_invoice(self, reference: str) -> dict | None:
        raise NotImplementedError()

    def get_settlements(
        self, from_date: datetime.date | None, to_date: datetime.date | None
    ) -> list[SettlementPayload]:
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
