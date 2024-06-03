import datetime
import logging
from typing import TYPE_CHECKING

import pydantic.v1 as pydantic_v1

import pcapi.core.finance.models as finance_models
import pcapi.core.finance.utils as finance_utils
from pcapi.routes.serialization import BaseModel


logger = logging.getLogger(__name__)


if TYPE_CHECKING:
    import pcapi.core.offerers.models as offerers_models


class FinanceBankAccountResponseModel(BaseModel):
    class Config:
        orm_mode = True

    id: int
    label: str


class FinanceBankAccountListResponseModel(BaseModel):
    __root__: list[FinanceBankAccountResponseModel]


class InvoiceListV2QueryModel(BaseModel):
    class Config:
        orm_mode = True

    periodBeginningDate: datetime.date | None
    periodEndingDate: datetime.date | None
    bankAccountId: int | None
    offererId: int | None


class InvoiceResponseV2Model(BaseModel):
    class Config:
        orm_mode = True

    reference: str
    date: datetime.date
    amount: float
    url: str
    bankAccountLabel: str | None
    cashflowLabels: list[str]

    @classmethod
    def from_orm(cls, invoice: finance_models.Invoice) -> "InvoiceResponseV2Model":
        invoice.bankAccountLabel = invoice.bankAccount.label
        invoice.cashflowLabels = [cashflow.batch.label for cashflow in invoice.cashflows]
        res = super().from_orm(invoice)
        res.amount = -finance_utils.to_euros(res.amount)  # type: ignore[assignment, arg-type]
        return res


class CombinedInvoiceListModel(BaseModel):
    invoiceReferences: list[str]

    @pydantic_v1.validator("invoiceReferences", pre=True)
    def ensure_list(cls, v: list[str] | str) -> list[str]:
        if isinstance(v, str):
            return [v]
        return v


class InvoiceListV2ResponseModel(BaseModel):
    __root__: list[InvoiceResponseV2Model]


class LinkedVenues(BaseModel):
    """A venue that is already linked to a bank account."""

    id: int
    commonName: str

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, venue: "offerers_models.Venue") -> "LinkedVenues":
        venue.commonName = venue.common_name
        return super().from_orm(venue)


class ManagedVenues(BaseModel):
    id: int
    commonName: str
    siret: str | None
    bankAccountId: int | None
    hasPricingPoint: bool

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, venue: "offerers_models.Venue") -> "ManagedVenues":
        """
        For each managed venue, we only want to display the current bank account
        that is linked to it, if any.
        """
        if len(venue.bankAccountLinks) > 1:
            logger.error("There should be one or no current bank account.", extra={"venue_id": venue.id})

        if venue.bankAccountLinks:
            venue.bankAccountId = venue.bankAccountLinks[0].bankAccountId
        venue.commonName = venue.common_name
        venue.hasPricingPoint = bool(venue.pricing_point_links)

        return super().from_orm(venue)


class BankAccountResponseModel(BaseModel):
    id: int
    isActive: bool
    label: str
    obfuscatedIban: str
    bic: str
    dsApplicationId: int | None
    status: finance_models.BankAccountApplicationStatus
    dateCreated: datetime.datetime
    dateLastStatusUpdate: datetime.datetime | None
    linkedVenues: list[LinkedVenues]

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, bank_account: finance_models.BankAccount) -> "BankAccountResponseModel":
        bank_account.linkedVenues = pydantic_v1.parse_obj_as(
            list[LinkedVenues], [link.venue for link in bank_account.venueLinks]
        )
        bank_account.obfuscatedIban = cls._obfuscate_iban(bank_account.iban)

        return super().from_orm(bank_account)

    @classmethod
    def _obfuscate_iban(cls, iban: str) -> str:
        return f"XXXX XXXX XXXX {iban[-4:]}"


class HasInvoiceQueryModel(BaseModel):
    offererId: int


class HasInvoiceResponseModel(BaseModel):
    hasInvoice: bool
