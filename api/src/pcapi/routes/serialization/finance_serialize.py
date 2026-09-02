import datetime
import logging
import typing

import pydantic as pydantic_v2
from pydantic import RootModel

from pcapi.core.finance import models
from pcapi.core.finance.utils import cents_to_full_unit
from pcapi.core.offerers import models as offerers_models
from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.serialization import HttpQueryParamsModel


logger = logging.getLogger(__name__)


# Query models
class InvoiceListV2QueryModel(HttpQueryParamsModel):
    period_beginning_date: datetime.date | None = None
    period_ending_date: datetime.date | None = None
    bank_account_id: int | None = None
    offerer_id: int | None = None
    amount_positive_only: bool | None = None
    amount_negative_only: bool | None = None


class HasInvoiceQueryModel(HttpQueryParamsModel):
    offerer_id: int


class HasSettlementQueryModel(HttpQueryParamsModel):
    offerer_id: int


class GetCombinedInvoicesQueryModel(HttpQueryParamsModel):
    invoice_references: list[str]

    @pydantic_v2.field_validator("invoice_references", mode="before")
    @classmethod
    def validate_list(cls, v: list[str] | str) -> list[str]:
        if isinstance(v, str):
            return [v]
        return v


class SettlementListQueryModel(HttpQueryParamsModel):
    offerer_id: int
    period_beginning_date: datetime.date | None = None
    period_ending_date: datetime.date | None = None
    bank_account_id: int | None = None
    name_search: str | None = None


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
    status: models.InvoiceStatus


class InvoiceListV2ResponseModel(RootModel):
    root: list[InvoiceResponseV2Model]


class SettlementResponseModel(HttpBodyModel):
    id: int
    label: str
    date: datetime.date | None
    amount: float
    bank_account: str
    status: models.SettlementStatus
    invoices_count: int

    @classmethod
    def build(cls, settlement: models.Settlement) -> typing.Self:
        return cls(
            id=settlement.id,
            label=settlement.batch.get_displayed_name(),
            date=settlement.batch.dateValidated.date() if settlement.batch.dateValidated else None,
            amount=float(cents_to_full_unit(settlement.amount)),
            bank_account=settlement.bankAccount.label,
            status=settlement.status,
            invoices_count=len(settlement.invoices),
        )


class SettlementListResponseModel(RootModel):
    root: list[SettlementResponseModel]


class LinkedVenue(HttpBodyModel):
    """A venue that is already linked to a bank account."""

    id: int
    publicName: str = pydantic_v2.Field(alias="commonName")
    state: offerers_models.VenueState | None


class ManagedVenue(HttpBodyModel):
    id: int
    name: str
    common_name: str
    siret: str | None
    bank_account_id: int | None
    has_pricing_point: bool
    state: offerers_models.VenueState | None


class BankAccountResponseModel(HttpBodyModel):
    id: int
    is_active: bool
    label: str
    iban: str = pydantic_v2.Field(alias="obfuscatedIban")
    ds_application_id: int | None
    status: models.BankAccountApplicationStatus
    date_created: datetime.datetime
    linked_venues: list[LinkedVenue]

    @pydantic_v2.field_validator("iban", mode="after")
    @classmethod
    def obfuscate_iban(cls, iban: str) -> str:
        return f"XXXX XXXX XXXX {iban[-4:]}"


class HasInvoiceResponseModel(HttpBodyModel):
    has_invoice: bool


class HasSettlementResponseModel(HttpBodyModel):
    has_settlement: bool
