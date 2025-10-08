import datetime
import logging
from typing import Any

import pydantic.v1 as pydantic_v1

import pcapi.core.finance.models as finance_models
import pcapi.core.finance.utils as finance_utils
from pcapi.routes.serialization import BaseModel
from pcapi.utils import date as date_utils


logger = logging.getLogger(__name__)


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
        res.amount = -finance_utils.cents_to_full_unit(res.amount)  # type: ignore[assignment, arg-type]
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


class LinnkedVenuesGetterDict(pydantic_v1.utils.GetterDict):
    def get(self, key: str, default: Any = None) -> Any:
        venue = self._obj
        if key == "commonName":
            return venue.common_name
        return super().get(key, default)


class LinkedVenues(BaseModel):
    """A venue that is already linked to a bank account."""

    id: int
    commonName: str

    class Config:
        orm_mode = True
        getter_dict = LinnkedVenuesGetterDict


class ManagedVenuesGetterDict(pydantic_v1.utils.GetterDict):
    def get(self, key: str, default: Any = None) -> Any:
        venue = self._obj
        if key == "commonName":
            return venue.common_name
        if key == "hasPricingPoint":
            return bool(venue.pricing_point_links)
        if key == "bankAccountId":
            if len(venue.bankAccountLinks) > 1:
                logger.error("There should be one or no current bank account.", extra={"venue_id": venue.id})
            if venue.bankAccountLinks:
                return venue.bankAccountLinks[0].bankAccountId
            return None
        return super().get(key, default)


class ManagedVenues(BaseModel):
    id: int
    name: str
    commonName: str
    siret: str | None
    bankAccountId: int | None
    hasPricingPoint: bool

    class Config:
        orm_mode = True
        getter_dict = ManagedVenuesGetterDict


class BankAccountResponseModel(BaseModel):
    id: int
    isActive: bool
    label: str
    obfuscatedIban: str
    dsApplicationId: int | None
    status: finance_models.BankAccountApplicationStatus
    dateCreated: datetime.datetime
    linkedVenues: list[LinkedVenues]

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, bank_account: finance_models.BankAccount) -> "BankAccountResponseModel":
        now = date_utils.get_naive_utc_now()
        bank_account.linkedVenues = pydantic_v1.parse_obj_as(
            list[LinkedVenues],
            [
                link.venue
                for link in bank_account.venueLinks
                if link.timespan.lower <= now
                and (not link.timespan.upper or now <= link.timespan.upper)
                and link.venue is not None  # ignore soft-deleted venues when the link is still active
            ],
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
