import datetime
from typing import Optional

from pydantic import BaseModel

import pcapi.core.finance.models as finance_models
import pcapi.serialization.utils as serialization_utils


class BusinessUnitResponseModel(BaseModel):
    id: int
    iban: str
    name: str
    siret: Optional[str]

    class Config:
        orm_mode = True


class ListBusinessUnitResponseModel(BaseModel):
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
        res.amount /= 100
        return res


class InvoiceListResponseModel(BaseModel):
    __root__: list[InvoiceResponseModel]


class BusinessUnitEditionBodyModel(BaseModel):
    class Config:
        alias_generator = serialization_utils.to_camel
        extra = "forbid"

    siret: str
