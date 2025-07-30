import datetime
import typing

import pydantic.v1 as pydantic_v1


class SireneAddress(pydantic_v1.BaseModel):
    if typing.TYPE_CHECKING:  # https://github.com/pydantic/pydantic/issues/156
        street: str
        postal_code: str
        city: str
        insee_code: str
    else:
        street: pydantic_v1.constr(strip_whitespace=True)
        postal_code: pydantic_v1.constr(strip_whitespace=True)
        city: pydantic_v1.constr(strip_whitespace=True)
        insee_code: pydantic_v1.constr(strip_whitespace=True)


class SirenInfo(pydantic_v1.BaseModel):
    if typing.TYPE_CHECKING:  # https://github.com/pydantic/pydantic/issues/156
        siren: str
        head_office_siret: str
    else:
        siren: pydantic_v1.constr(strip_whitespace=True, min_length=9, max_length=9)
        head_office_siret: pydantic_v1.constr(strip_whitespace=True, min_length=14, max_length=14)
    name: str
    ape_code: str | None
    ape_label: str | None = None  # optional, set only from API Entreprise
    active: bool
    diffusible: bool
    legal_category_code: str
    address: SireneAddress | None
    creation_date: datetime.date | None
    closure_date: datetime.date | None = None


class SiretInfo(pydantic_v1.BaseModel):
    if typing.TYPE_CHECKING:  # https://github.com/pydantic/pydantic/issues/156
        siret: str
        siren: str | None
    else:
        siret: pydantic_v1.constr(strip_whitespace=True, min_length=14, max_length=14)
        siren: pydantic_v1.constr(strip_whitespace=True, min_length=9, max_length=9) | None
    active: bool
    diffusible: bool
    name: str
    address: SireneAddress
    ape_code: str | None
    ape_label: str | None = None  # optional, set only from API Entreprise
    legal_category_code: str


class RCSCorporateOfficer(pydantic_v1.BaseModel):
    name: str
    role: str | None


class RCSObservation(pydantic_v1.BaseModel):
    date: datetime.date | None
    label: str


class RCSInfo(pydantic_v1.BaseModel):
    registered: bool
    # Next fields set only when registered
    registration_date: datetime.date | None = None
    deregistration_date: datetime.date | None = None
    head_office_activity: str | None = None
    corporate_officers: list[RCSCorporateOfficer] | None = None
    observations: list[RCSObservation] | None = None


class UrssafInfo(pydantic_v1.BaseModel):
    attestation_delivered: bool
    details: str
    # Next fields set only when attestation is delivered
    validity_start_date: datetime.date | None = None
    validity_end_date: datetime.date | None = None
    verification_code: str | None = None


class DgfipInfo(pydantic_v1.BaseModel):
    attestation_delivered: bool
    # Next fields set only when attestation is delivered
    attestation_date: datetime.date | None = None
    verified_date: datetime.date | None = None
