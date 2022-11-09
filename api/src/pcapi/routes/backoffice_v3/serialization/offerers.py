import pcapi.core.offerers.models as offerers_models
from pcapi.routes.serialization import BaseModel


class OffererBankInformationStatus(BaseModel):
    """
    le nombre de lieux dont les infos permettent (ok), ou pas (ko), les remboursements
    """

    ko: int
    ok: int


class OffererBasicInfo(BaseModel):
    class Config:
        use_enum_values = True

    id: int
    name: str
    validation_status: offerers_models.ValidationStatus
    isActive: bool
    siren: str | None
    region: str
    bank_information_status: OffererBankInformationStatus
    is_collective_eligible: bool


class BaseOffersStats(BaseModel):
    individual: int
    collective: int


class OffersStats(BaseModel):
    active: BaseOffersStats
    inactive: BaseOffersStats
