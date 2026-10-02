import datetime
import enum
import logging
import typing
from dataclasses import dataclass

import pydantic
from pydantic import RootModel

from pcapi.core.finance import models
from pcapi.core.finance.utils import cents_to_full_unit
from pcapi.core.offerers import models as offerers_models
from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.serialization import HttpQueryParamsModel
from pcapi.utils.date import get_naive_utc_now


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

    @pydantic.field_validator("invoice_references", mode="before")
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
    name_search: str | None = pydantic.Field(default=None, min_length=1)


class GetRejectedBankAccountsQueryModel(HttpQueryParamsModel):
    offerer_id: int


# Response Models


class InvoiceResponseV2Model(HttpBodyModel):
    reference: str
    date: datetime.date
    amount: float
    url: str
    status: models.InvoiceStatus

    @classmethod
    def build(cls, invoice: models.Invoice) -> typing.Self:
        return cls(
            reference=invoice.reference,
            date=invoice.date.date(),
            amount=float(-cents_to_full_unit(invoice.amount)),
            url=invoice.url,
            status=invoice.status,
        )


class InvoiceListV2ResponseModel(RootModel):
    root: list[InvoiceResponseV2Model]


class SettlementDisplayedStatus(enum.Enum):
    EXECUTED = "EXECUTED"
    REJECTED_UNRESOLVED = "REJECTED_UNRESOLVED"
    REJECTED_PROCESSED = "REJECTED_PROCESSED"
    REJECTED_SOLVED = "REJECTED_SOLVED"


@dataclass
class SettlementData:
    displayed_status: SettlementDisplayedStatus
    resolving_settlements: list[models.Settlement]
    detached_venues: list[offerers_models.Venue]


def get_settlement_data(settlement: models.Settlement) -> SettlementData:
    """
    Note: when a settlement is rejected, the corresponding bank account becomes invalid and the venues are detached from the bank account

    displayed_status is:
    - EXECUTED = the settlement is not rejected
    - REJECTED_SOLVED = the settlement is rejected and the invoices are linked to a new (non-rejected) settlement
    - REJECTED_UNRESOLVED = the settlement is rejected and the venues previously linked to the bank account are not linked to another bank account
    - REJECTED_PROCESSED = the settlement is rejected and the venues are linked to another bank account

    resolving_settlements are the settlements that "resolve" the current one, i.e that include its invoices
    (filled only when displayed_status is REJECTED_SOLVED)

    detached_venues are the venues previously linked to the settlement bank account and that are not currently linked to another account
    (filled only when displayed_status is REJECTED_UNRESOLVED)

    Note: this "python-side" processing trades efficiency for clarity
    If a performance issue appears, the logic can be translated in SQL
    """
    now = get_naive_utc_now()

    if settlement.status != models.SettlementStatus.REJECTED:
        return SettlementData(
            displayed_status=SettlementDisplayedStatus.EXECUTED, resolving_settlements=[], detached_venues=[]
        )

    # check if the rejected settlement invoices have been paid by another settlement
    resolving_settlements = []
    for invoice in settlement.invoices:
        resolving_settlement = next(
            (s for s in invoice.settlements if s.status == models.SettlementStatus.EXECUTED), None
        )

        if resolving_settlement:
            resolving_settlements.append(resolving_settlement)
        else:
            # the invoice is not linked to any valid settlement -> the settlement will not be "solved"
            break

    if len(resolving_settlements) == len(settlement.invoices):
        # all invoices are linked to a valid settlement
        return SettlementData(
            displayed_status=SettlementDisplayedStatus.REJECTED_SOLVED,
            resolving_settlements=resolving_settlements,
            detached_venues=[],
        )

    # check that all detached venues are linked to another bank account
    detached_venues = settlement.bankAccount.get_detached_venues_at(now)
    if detached_venues:
        return SettlementData(
            displayed_status=SettlementDisplayedStatus.REJECTED_UNRESOLVED,
            resolving_settlements=[],
            detached_venues=detached_venues,
        )

    # all venues are linked to a valid bank account, but an invoice is not yet processed
    return SettlementData(
        displayed_status=SettlementDisplayedStatus.REJECTED_PROCESSED, resolving_settlements=[], detached_venues=[]
    )


class SettlementResponseModel(HttpBodyModel):
    id: int
    label: str
    date: datetime.date | None
    amount: float
    bank_account: str
    status: SettlementDisplayedStatus
    invoices: list[InvoiceResponseV2Model]
    resolved_by: list[str]

    @classmethod
    def build(cls, settlement: models.Settlement) -> typing.Self:
        # show paid invoices only and sort in sync with the GET invoices route
        invoices = sorted(
            (invoice for invoice in settlement.invoices if invoice.status == models.InvoiceStatus.PAID),
            key=lambda i: i.date,
            reverse=True,
        )

        if settlement.amount > 0:  # settlement paid by offerer
            return cls(
                id=settlement.id,
                label="-",
                date=settlement.settlementDate,
                amount=float(-cents_to_full_unit(settlement.amount)),
                bank_account=settlement.bankAccount.label,
                status=SettlementDisplayedStatus.EXECUTED,
                invoices=[InvoiceResponseV2Model.build(invoice) for invoice in invoices],
                resolved_by=[],
            )

        settlement_data = get_settlement_data(settlement)
        resolved_by = {s.batch.get_displayed_name() for s in settlement_data.resolving_settlements}  # type: ignore[union-attr]
        assert settlement.batch  # outgoing batch must have a batch

        return cls(
            id=settlement.id,
            label=settlement.batch.get_displayed_name(),
            date=settlement.batch.dateValidated.date() if settlement.batch.dateValidated else None,
            amount=float(-cents_to_full_unit(settlement.amount)),
            bank_account=settlement.bankAccount.label,
            status=settlement_data.displayed_status,
            invoices=[InvoiceResponseV2Model.build(invoice) for invoice in invoices],
            resolved_by=sorted(resolved_by),
        )


class SettlementListResponseModel(RootModel):
    root: list[SettlementResponseModel]


class LinkedVenue(HttpBodyModel):
    """A venue that is already linked to a bank account."""

    id: int
    publicName: str = pydantic.Field(alias="commonName")
    state: offerers_models.VenueState | None


class ManagedVenue(HttpBodyModel):
    id: int
    name: str
    common_name: str
    siret: str | None
    bank_account_id: int | None
    has_pricing_point: bool
    state: offerers_models.VenueState | None


def _obfuscate_iban(iban: str) -> str:
    return f"XXXX XXXX XXXX {iban[-4:]}"


class BankAccountResponseModel(HttpBodyModel):
    id: int
    is_active: bool
    label: str
    iban: str = pydantic.Field(alias="obfuscatedIban")
    ds_application_id: int | None
    status: models.BankAccountApplicationStatus
    date_created: datetime.datetime
    linked_venues: list[LinkedVenue]

    @pydantic.field_validator("iban", mode="after")
    @classmethod
    def obfuscate_iban(cls, iban: str) -> str:
        return _obfuscate_iban(iban)


class DetachedVenueResponseModel(HttpBodyModel):
    id: int
    publicName: str


class RejectedBankAccountResponseModel(HttpBodyModel):
    id: int
    label: str
    obfuscatedIban: str
    rejectedSettlementLabel: str
    detachedVenues: list[DetachedVenueResponseModel]

    @classmethod
    def build(
        cls,
        bank_account: models.BankAccount,
        rejected_settlement_label: str,
        detached_venues: list[offerers_models.Venue],
    ) -> typing.Self:
        return cls(
            id=bank_account.id,
            label=bank_account.label,
            obfuscatedIban=_obfuscate_iban(bank_account.iban),
            rejectedSettlementLabel=rejected_settlement_label,
            detachedVenues=[DetachedVenueResponseModel.model_validate(venue) for venue in detached_venues],
        )


class RejectedBankAccountsResponseModel(RootModel):
    root: list[RejectedBankAccountResponseModel]


class HasInvoiceResponseModel(HttpBodyModel):
    has_invoice: bool


class HasSettlementResponseModel(HttpBodyModel):
    has_settlement: bool
