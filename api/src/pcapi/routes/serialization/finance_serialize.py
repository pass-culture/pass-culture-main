import datetime
import logging

import pydantic as pydantic_v2
from pydantic import RootModel

import pcapi.core.finance.models as finance_models
from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.serialization import HttpQueryParamsModel


logger = logging.getLogger(__name__)


# Query models
class InvoiceListV2QueryModel(HttpQueryParamsModel):
    period_beginning_date: datetime.date | None = None
    period_ending_date: datetime.date | None = None
    bank_account_id: int | None = None
    offerer_id: int | None = None


class HasInvoiceQueryModel(HttpQueryParamsModel):
    offerer_id: int


class GetCombinedInvoicesQueryModel(HttpQueryParamsModel):
    invoice_references: list[str]

    @pydantic_v2.field_validator("invoice_references", mode="before")
    @classmethod
    def validate_list(cls, v: list[str] | str) -> list[str]:
        if isinstance(v, str):
            return [v]
        return v


# Response Models
class FinanceBankAccountResponseModel(HttpBodyModel):
    id: int
    label: str


class FinanceBankAccountListResponseModel(RootModel):
    root: list[FinanceBankAccountResponseModel]


class InvoiceResponseV2Model(HttpBodyModel):
    reference: str
    date: datetime.date
    amount: float
    url: str
    bank_account_label: str | None
    cashflow_labels: list[str]


class InvoiceListV2ResponseModel(RootModel):
    root: list[InvoiceResponseV2Model]


class LinkedVenue(HttpBodyModel):
    """A venue that is already linked to a bank account."""

    id: int
    common_name: str


class ManagedVenue(HttpBodyModel):
    id: int
    name: str
    common_name: str
    siret: str | None
    bank_account_id: int | None
    has_pricing_point: bool


class BankAccountResponseModel(HttpBodyModel):
    id: int
    is_active: bool
    label: str
    iban: str = pydantic_v2.Field(alias="obfuscatedIban")
    ds_application_id: int | None
    status: finance_models.BankAccountApplicationStatus
    date_created: datetime.datetime
    linked_venues: list[LinkedVenue]

    @pydantic_v2.field_validator("iban", mode="after")
    @classmethod
    def obfuscate_iban(cls, iban: str) -> str:
        return f"XXXX XXXX XXXX {iban[-4:]}"


class HasInvoiceResponseModel(HttpBodyModel):
    has_invoice: bool
