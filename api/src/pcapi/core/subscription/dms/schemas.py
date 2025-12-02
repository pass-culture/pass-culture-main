import datetime
import enum

import pydantic.v1 as pydantic_v1

from pcapi.core.subscription import schemas as subscription_schemas
from pcapi.core.users import models as users_models


class DmsAnnotation(pydantic_v1.BaseModel):
    id: str
    label: str
    text: str | None


class DmsInstructorAnnotationEnum(enum.Enum):
    NEL = "NEL"  # Non éligible
    S = "S"  # Selfie (absent ou illisible)
    NC = "NC"  # Non Conforme
    EC = "EC"  # Erreur civilité (prénom, nom)
    JD = "JD"  # Justificatif de domicile < 1 an
    AH = "AH"  # Attestation d'Hébergement
    AD = "AD"  # Adresse
    DN = "DN"  # Date de naissance
    LN = "LN"  # Lieu de naissance
    IDM = "IDM"  # ID manquante
    IDN = "IDN"  # Erreur n° ID
    IDP = "IDP"  # ID périmée
    IDH = "IDH"  # ID de l'hébergeur
    CD = "CD"  # Couverture documentaire


class DmsInstructorAnnotation(pydantic_v1.BaseModel):
    # Support multiple choices and legacy single choice (when parsing DMSContent in saved applications)
    value: list[DmsInstructorAnnotationEnum] | DmsInstructorAnnotationEnum
    updated_datetime: datetime.datetime | None


class DmsFieldErrorKeyEnum(enum.Enum):
    birth_date = "birth_date"
    first_name = "first_name"
    id_piece_number = "id_piece_number"
    last_name = "last_name"
    postal_code = "postal_code"


class DmsFieldErrorDetails(pydantic_v1.BaseModel):
    key: DmsFieldErrorKeyEnum
    value: str | None


class DMSContent(subscription_schemas.IdentityCheckContent):
    activity: str | None
    address: str | None
    annotation: DmsAnnotation | None
    application_number: int = pydantic_v1.Field(..., alias="application_id")  # keep alias for old data
    birth_date: datetime.date | None
    birth_place: str | None
    city: str | None
    civility: users_models.GenderEnum | None
    deletion_datetime: datetime.datetime | None
    department: str | None  # this field is not filled anymore
    email: str
    field_errors: list[DmsFieldErrorDetails] | None
    first_name: str
    id_piece_number: str | None
    instructor_annotation: DmsInstructorAnnotation | None
    last_name: str
    latest_modification_datetime: datetime.datetime | None
    latest_user_fields_modification_datetime: datetime.datetime | None
    phone: str | None
    postal_code: str | None
    procedure_number: int = pydantic_v1.Field(..., alias="procedure_id")  # keep alias for old data
    processed_datetime: datetime.datetime | None
    registration_datetime: datetime.datetime | None
    state: str | None

    class Config:
        allow_population_by_field_name = True

    def get_activity(self) -> str | None:
        return self.activity

    def get_address(self) -> str | None:
        return self.address

    def get_birth_date(self) -> datetime.date | None:
        return self.birth_date

    def get_birth_place(self) -> str | None:
        return self.birth_place

    def get_civility(self) -> str | None:
        return self.civility.value if self.civility else None

    def get_city(self) -> str | None:
        return self.city

    def get_first_name(self) -> str:
        return self.first_name

    def get_id_piece_number(self) -> str | None:
        return self.id_piece_number

    def get_last_name(self) -> str:
        return self.last_name

    def get_latest_modification_datetime(self) -> datetime.datetime | None:
        return self.latest_modification_datetime

    def get_phone_number(self) -> str | None:
        return self.phone

    def get_postal_code(self) -> str | None:
        return self.postal_code

    def get_registration_datetime(self) -> datetime.datetime | None:
        return self.registration_datetime
