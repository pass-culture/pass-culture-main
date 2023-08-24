import datetime

from pcapi.routes.serialization import BaseModel


class VenueBankInformation(BaseModel):
    pricing_point_name: str | None
    pricing_point_url: str | None
    reimbursement_point_name: str | None
    reimbursement_point_url: str | None
    bic: str | None
    iban: str | None


class VenueDmsStats(BaseModel):
    status: str
    subscriptionDate: datetime.datetime
    lastChangeDate: datetime.datetime
    url: str
