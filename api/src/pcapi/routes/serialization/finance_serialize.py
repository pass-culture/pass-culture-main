import datetime

import pcapi.core.finance.models as finance_models
import pcapi.core.finance.utils as finance_utils
from pcapi.routes.serialization import BaseModel
import pcapi.serialization.utils as serialization_utils


class BusinessUnitListQueryModel(BaseModel):
    class Config:
        alias_generator = serialization_utils.to_camel
        extra = "forbid"

    _dehumanize_id = serialization_utils.dehumanize_field("offerer_id")
    offerer_id: int | None


class BusinessUnitResponseModel(BaseModel):
    class Config:
        orm_mode = True

    id: int
    iban: str | None
    bic: str | None
    name: str
    # FIXME (dbaty, 2021-12-15): SIRET may be NULL while we initialize
    # business units. In a few months, all business units should have
    # a SIRET and we should remove `Optional`.
    siret: str | None

    @classmethod
    def from_orm(cls, business_unit: finance_models.BusinessUnit):  # type: ignore [no-untyped-def]
        business_unit.iban = business_unit.bankAccount.iban
        business_unit.bic = business_unit.bankAccount.bic
        res = super().from_orm(business_unit)
        return res


class BusinessUnitListResponseModel(BaseModel):
    __root__: list[BusinessUnitResponseModel]

    class Config:
        orm_mode = True


class InvoiceListQueryModel(BaseModel):
    class Config:
        orm_mode = True

    businessUnitId: int | None
    periodBeginningDate: datetime.date | None
    periodEndingDate: datetime.date | None


class InvoiceResponseModel(BaseModel):
    class Config:
        orm_mode = True

    reference: str
    date: datetime.date
    amount: float
    url: str
    businessUnitName: str
    cashflowLabels: list[str]

    @classmethod
    def from_orm(cls, invoice: finance_models.Invoice):  # type: ignore [no-untyped-def]
        invoice.businessUnitName = invoice.businessUnit.name
        invoice.cashflowLabels = [cashflow.batch.label for cashflow in invoice.cashflows]
        res = super().from_orm(invoice)
        res.amount = -finance_utils.to_euros(res.amount)  # type: ignore [assignment, arg-type]
        return res


class InvoiceListResponseModel(BaseModel):
    __root__: list[InvoiceResponseModel]


class BusinessUnitEditionBodyModel(BaseModel):
    class Config:
        alias_generator = serialization_utils.to_camel
        extra = "forbid"

    siret: str
