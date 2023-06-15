import datetime

import pcapi.core.finance.models as finance_models
import pcapi.core.finance.utils as finance_utils
from pcapi.routes.serialization import BaseModel


class FinanceReimbursementPointResponseModel(BaseModel):
    class Config:
        orm_mode = True

    id: int
    name: str
    publicName: str | None


class FinanceReimbursementPointListResponseModel(BaseModel):
    __root__: list[FinanceReimbursementPointResponseModel]


class InvoiceListQueryModel(BaseModel):
    class Config:
        orm_mode = True

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
    reimbursementPointName: str | None
    cashflowLabels: list[str]

    @classmethod
    def from_orm(cls, invoice: finance_models.Invoice) -> "InvoiceResponseModel":
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
