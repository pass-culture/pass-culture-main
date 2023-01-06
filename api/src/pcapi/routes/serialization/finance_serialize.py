import datetime

import pcapi.core.finance.models as finance_models
import pcapi.core.finance.utils as finance_utils
from pcapi.routes.serialization import BaseModel
import pcapi.serialization.utils as serialization_utils


class BusinessUnitListQueryModel(BaseModel):
    # FIXME (mageoffray, 2022-12-27): Business Units are not used and this should be cleaned
    # Please do not use dehumanize anymore.
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
    def from_orm(cls, business_unit: finance_models.BusinessUnit) -> "BusinessUnitResponseModel":
        business_unit.iban = business_unit.bankAccount.iban  # type: ignore [union-attr]
        business_unit.bic = business_unit.bankAccount.bic  # type: ignore [union-attr]
        res = super().from_orm(business_unit)
        return res


class BusinessUnitListResponseModel(BaseModel):
    __root__: list[BusinessUnitResponseModel]

    class Config:
        orm_mode = True


class ReimbursementPointListQueryModel(BaseModel):
    class Config:
        alias_generator = serialization_utils.to_camel
        extra = "forbid"

    _dehumanize_id = serialization_utils.dehumanize_field("offerer_id")
    offerer_id: int | None


class ReimbursementPointResponseModel(BaseModel):
    class Config:
        orm_mode = True

    id: int
    name: str
    publicName: str | None


class ReimbursementPointListResponseModel(BaseModel):
    __root__: list[ReimbursementPointResponseModel]


class InvoiceListQueryModel(BaseModel):
    class Config:
        orm_mode = True

    businessUnitId: int | None
    periodBeginningDate: datetime.date | None
    periodEndingDate: datetime.date | None
    reimbursementPointId: int | None


class InvoiceResponseModel(BaseModel):
    class Config:
        orm_mode = True

    reference: str
    date: datetime.date
    amount: float
    url: str
    businessUnitName: str | None
    reimbursementPointName: str | None
    cashflowLabels: list[str]

    @classmethod
    def from_orm(cls, invoice: finance_models.Invoice) -> "InvoiceResponseModel":
        invoice.businessUnitName = invoice.businessUnit.name if invoice.businessUnit else None
        invoice.reimbursementPointName = (
            (invoice.reimbursementPoint.publicName or invoice.reimbursementPoint.name)
            if invoice.reimbursementPoint
            else None
        )
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
