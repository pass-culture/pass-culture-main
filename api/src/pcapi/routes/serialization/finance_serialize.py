import datetime
from typing import Optional

import pcapi.core.finance.models as finance_models
import pcapi.core.finance.utils as finance_utils
from pcapi.routes.serialization import BaseModel
import pcapi.serialization.utils as serialization_utils


class BusinessUnitListQueryModel(BaseModel):
    class Config:
        alias_generator = serialization_utils.to_camel
        extra = "forbid"

    _dehumanize_id = serialization_utils.dehumanize_field("offerer_id")
    offerer_id: Optional[int]


class BusinessUnitResponseModel(BaseModel):
    class Config:
        orm_mode = True

    id: int
    iban: Optional[str]
    bic: Optional[str]
    name: str
    # FIXME (dbaty, 2021-12-15): SIRET may be NULL while we initialize
    # business units. In a few months, all business units should have
    # a SIRET and we should remove `Optional`.
    siret: Optional[str]

    @classmethod
    def from_orm(cls, business_unit: finance_models.BusinessUnit):
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

    businessUnitId: Optional[int]
    periodBeginningDate: Optional[datetime.date]
    periodEndingDate: Optional[datetime.date]


class InvoiceResponseModel(BaseModel):
    class Config:
        orm_mode = True

    reference: str
    date: datetime.date
    amount: float
    url: str
    businessUnitName: str

    @classmethod
    def from_orm(cls, invoice: finance_models.Invoice):
        invoice.businessUnitName = invoice.businessUnit.name
        res = super().from_orm(invoice)
        res.amount = -finance_utils.to_euros(res.amount)
        return res


class InvoiceListResponseModel(BaseModel):
    __root__: list[InvoiceResponseModel]


class BusinessUnitEditionBodyModel(BaseModel):
    class Config:
        alias_generator = serialization_utils.to_camel
        extra = "forbid"

    siret: str
