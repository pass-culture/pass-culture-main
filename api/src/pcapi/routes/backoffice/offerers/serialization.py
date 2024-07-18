from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.routes.serialization import BaseModel
from pydantic import ConfigDict


class OffererBankInformationStatus(BaseModel):
    """
    le nombre de lieux dont les infos permettent (ok), ou pas (ko), les remboursements
    """

    ko: int
    ok: int


class OffererBasicInfo(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    id: int
    name: str
    validation_status: ValidationStatus
    isActive: bool
    siren: str | None
    region: str
    bank_information_status: OffererBankInformationStatus
