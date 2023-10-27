from pcapi.routes.serialization import BaseModel


class VenueBankInformation(BaseModel):
    pricing_point_name: str | None
    pricing_point_url: str | None
    reimbursement_point_name: str | None
    reimbursement_point_url: str | None
    bic: str | None
    iban: str | None
